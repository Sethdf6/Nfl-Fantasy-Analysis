import requests
import time
import random
from bs4 import BeautifulSoup
import pandas as pd
import re

# —————— Setup ——————————————————————————————————————————————

# ESPN blocks bots by default, so we’ll send a desktop UA
session = requests.Session()
session.headers.update({
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/114.0.0.0 Safari/537.36'
    )
})

# list of (ESPN abbr, slug) for all 32 teams
teams = [
    ('ari','arizona-cardinals'),
    ('atl','atlanta-falcons'),
    ('bal','baltimore-ravens'),
    ('buf','buffalo-bills'),
    ('car','carolina-panthers'),
    ('chi','chicago-bears'),
    ('cin','cincinnati-bengals'),
    ('cle','cleveland-browns'),
    ('dal','dallas-cowboys'),
    ('den','denver-broncos'),
    ('det','detroit-lions'),
    ('gb','green-bay-packers'),
    ('hou','houston-texans'),
    ('ind','indianapolis-colts'),
    ('jax','jacksonville-jaguars'),
    ('kc','kansas-city-chiefs'),
    ('lv','las-vegas-raiders'),
    ('lac','los-angeles-chargers'),
    ('lar','los-angeles-rams'),
    ('mia','miami-dolphins'),
    ('min','minnesota-vikings'),
    ('ne','new-england-patriots'),
    ('no','new-orleans-saints'),
    ('nyg','new-york-giants'),
    ('nyj','new-york-jets'),
    ('phi','philadelphia-eagles'),
    ('pit','pittsburgh-steelers'),
    ('sea','seattle-seahawks'),
    ('sf','san-francisco-49ers'),
    ('tb','tampa-bay-buccaneers'),
    ('ten','tennessee-titans'),
    ('wsh','washington-commanders'),
]

# mapping from ESPN slug to your desired 3-letter code
team_mapping = {
    'arizona-cardinals':   'ARI',
    'atlanta-falcons':     'ATL',
    'baltimore-ravens':    'BAL',
    'buffalo-bills':       'BUF',
    'carolina-panthers':   'CAR',
    'chicago-bears':       'CHI',
    'cincinnati-bengals':  'CIN',
    'cleveland-browns':    'CLE',
    'dallas-cowboys':      'DAL',
    'denver-broncos':      'DEN',
    'detroit-lions':       'DET',
    'green-bay-packers':   'GNB',
    'houston-texans':      'HOU',
    'indianapolis-colts':  'IND',
    'jacksonville-jaguars':'JAX',
    'kansas-city-chiefs':  'KAN',
    'los-angeles-chargers':'LAC',
    'los-angeles-rams':    'LAR',
    'las-vegas-raiders':   'LVR',
    'miami-dolphins':      'MIA',
    'minnesota-vikings':   'MIN',
    'new-england-patriots':'NWE',
    'new-orleans-saints':  'NOR',
    'new-york-giants':     'NYG',
    'new-york-jets':       'NYJ',
    'philadelphia-eagles': 'PHI',
    'pittsburgh-steelers': 'PIT',
    'seattle-seahawks':    'SEA',
    'san-francisco-49ers': 'SFO',
    'tampa-bay-buccaneers':'TAM',
    'tennessee-titans':    'TEN',
    'washington-commanders':'WAS',
}

def parse_html_table(table_tag):
    """
    Simple parser for tables with a single header row.
    """
    # extract header names
    headers = [th.get_text(strip=True) for th in table_tag.find('thead').find_all('th')]
    # extract rows
    data = []
    for tr in table_tag.find('tbody').find_all('tr'):
        cells = [td.get_text(strip=True) for td in tr.find_all('td')]
        if len(cells) == len(headers):
            data.append(cells)
    return pd.DataFrame(data, columns=headers)

# —————— Scrape & Combine ——————————————————————————————————

all_dfs = []

for abbr, slug in teams:
    url = f"https://www.espn.com/nfl/team/roster/_/name/{abbr}/{slug}"
    print(f"Fetching {slug} …", end=" ")
    resp = session.get(url)
    if resp.status_code != 200:
        print(f"→ HTTP {resp.status_code}, skipping")
        continue

    soup = BeautifulSoup(resp.text, 'html.parser')
    table = soup.find('table')
    if not table:
        print("→ no table found, skipping")
        continue

    df = parse_html_table(table)
    # attach the 3-letter team code
    team_code = team_mapping.get(slug, abbr.upper())
    df['Team'] = team_code

    all_dfs.append(df)
    print(f"→ found {len(df)} players")

    # polite pause
    time.sleep(random.uniform(1, 2))

# concatenate and save
if all_dfs:
    combined = pd.concat(all_dfs, ignore_index=True)
    combined.to_csv("all_nfl_rosters.csv", index=False)
    print(f"\nSaved all rosters to all_nfl_rosters.csv ({combined.shape[0]} rows × {combined.shape[1]} cols)")
else:
    print("No data collected.")
