import os
import re
import time
import string
import random
import requests
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm

# ──────────────────────────────────────────────────────────────────────────────
BASE_URL        = 'https://www.pro-football-reference.com'
LETTERS         = list(string.ascii_uppercase)
VALID_POSITIONS = {'QB', 'RB', 'WR', 'TE', 'K'}
START_YEAR      = 2005
END_YEAR        = 2025

HEADERS     = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36'
    )
}
MAX_RETRIES = 3

CSV_DIR = 'csv_data'
# ──────────────────────────────────────────────────────────────────────────────

os.makedirs(CSV_DIR, exist_ok=True)
print("Running in directory:", os.getcwd())
print("Will write CSVs into:", os.path.abspath(CSV_DIR))

session = requests.Session()

def fetch_url(url: str) -> str:
    """GET a URL, retrying forever on network errors, wait 4–5s between tries.
    Return the page text on HTTP 200, or empty string on any other status."""
    while True:
        try:
            resp = session.get(url, headers=HEADERS, timeout=30)
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Network error for {url}: {e}. Retrying in 5s…")
            time.sleep(5)
            continue

        # if we got here, no network exception
        time.sleep(random.uniform(4, 5))
        if resp.status_code == 200:
            return resp.text
        else:
            print(f"❌ [{resp.status_code}] GET {url} – giving up on this URL")
            return ""


def get_players_for_letter(letter: str):
    url  = f"{BASE_URL}/players/{letter}/"
    html = fetch_url(url)
    if not html:
        return []

    soup    = BeautifulSoup(html, 'html.parser')
    all_div = soup.find('div', id='all_players')
    if not all_div:
        return []

    players = []
    for p in all_div.find_all('p'):
        a = p.find('a', href=True)
        if not a:
            continue

        href = a['href']
        m    = re.match(r"/players/[A-Z]/(.+)\.htm", href)
        if not m:
            continue
        code = m.group(1)
        name = a.text.strip()

        details = p.text.replace(name, "", 1).strip()
        dm = re.match(r"^\((?P<pos>[^)]+)\)\s*(?P<years>\d{4}(?:-\d{0,4})?)", details)
        if not dm:
            continue

        pos = dm.group('pos').strip()
        yrs = dm.group('years')
        if '-' in yrs:
            y_min, y_max = yrs.split('-', 1)
            y_min = int(y_min)
            y_max = int(y_max) if y_max else END_YEAR
        else:
            y_min = y_max = int(yrs)

        if pos not in VALID_POSITIONS or y_max < START_YEAR or y_min > END_YEAR:
            continue

        players.append({
            'name':     name,
            'letter':   letter,
            'code':     code,
            'pos':      pos,
            'year_min': y_min,
            'year_max': y_max
        })

    return players

def fetch_gamelog(player, year):
    """Fetch one player's gamelog for a given year, flattening its two-row header."""
    url  = f"{BASE_URL}/players/{player['letter']}/{player['code']}/gamelog/{year}/"
    html = fetch_url(url)
    if not html:
        return None

    # strip out PFR's HTML comments around the table
    clean = html.replace("<!--", "").replace("-->", "")
    soup  = BeautifulSoup(clean, 'html.parser')
    tbl   = soup.find('table', id='gamelog') or soup.find('table', id='stats')
    if tbl is None:
        return None

    # read with a two-row header
    try:
        df = pd.read_html(str(tbl), header=[0,1])[0]
    except ValueError:
        # fallback if there's only a single header row
        df = pd.read_html(str(tbl), header=0)[0]

    # now flatten the MultiIndex (or single-level) into clean names
    cols = []
    for top, sub in df.columns:
        top = str(top).strip()
        sub = str(sub).strip()
        if sub.lower().startswith('unnamed') or not sub:
            cols.append(top)
        elif top.lower().startswith('unnamed') or not top:
            cols.append(sub)
        else:
            cols.append(f"{top} {sub}")
    df.columns = cols

    # drop any fully-empty columns
    df = df.loc[:, df.columns.notna()]

    df['Player']   = player['name']
    df['Position'] = player['pos']
    df['Year']     = year

    return df

def main():
    # bucket DataFrames by position
    pos_data = {pos: [] for pos in VALID_POSITIONS}

    for letter in tqdm(LETTERS, desc="Letters"):
        players = get_players_for_letter(letter)
        for pl in tqdm(players, desc=f"Players {letter}", leave=False):
            for yr in range(max(pl['year_min'], START_YEAR),
                            min(pl['year_max'], END_YEAR) + 1):
                df = fetch_gamelog(pl, yr)
                if df is not None:
                    pos_data[pl['pos']].append(df)
        time.sleep(1)  # a courteous pause

    # write one CSV per position, each with its own real headers
    for pos, dfs in pos_data.items():
        if dfs:
            combined = pd.concat(dfs, sort=False, ignore_index=True)
            path     = os.path.join(CSV_DIR, f"pfr_gamelogs_{pos}.csv")
            combined.to_csv(path, index=False)
            print(f"✅ Wrote {len(combined)} rows for {pos} → {path}")
        else:
            print(f"⚠️  No data for {pos}, skipping.")

if __name__ == "__main__":
    main()
