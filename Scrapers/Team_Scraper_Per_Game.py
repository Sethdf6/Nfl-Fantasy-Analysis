#!/usr/bin/env python3
import os
import time
import random
import requests
import pandas as pd
from bs4 import BeautifulSoup

# ─── 1) CONFIG ────────────────────────────────────────────────────────────────
BASE       = "https://www.pro-football-reference.com"
YEARS      = range(2006, 2025)
TEAMS      = [
    'crd','atl','rav','buf','car','chi','cin','cle','dal','den','det',
    'gnb','htx','clt','jax','kan','sdg','ram','rai','mia','min','nwe',
    'nor','nyg','nyj','phi','pit','sea','sfo','tam','oti','was'
]
HEADERS    = {"User-Agent": "Mozilla/5.0"}
OUT_DIR    = "team_game_logs"
os.makedirs(OUT_DIR, exist_ok=True)

# ─── 2) SESSION + BACKOFF ────────────────────────────────────────────────────
session = requests.Session()
session.trust_env = False

def fetch_url(url, retries=3):
    """GET with simple exponential backoff on 429/503."""
    for i in range(retries):
        r = session.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            return r
        if r.status_code in (429, 503):
            wait = (2**i) + random.random()
            print(f"{r.status_code} at {url}, retry in {wait:.1f}s")
            time.sleep(wait)
            continue
        print(f"Error {r.status_code} fetching {url}")
        return None
    print(f"Failed to fetch {url} after {retries} retries")
    return None

# ─── 3) FLATTEN MULTIINDEX HEADER ─────────────────────────────────────────────
def flatten_multiindex(df):
    if not isinstance(df.columns, pd.MultiIndex):
        return df
    df.columns = [
        f"{str(top).strip()} {str(sub).strip()}".strip()
        for top, sub in df.columns
    ]
    return df

# ─── 4) DOWNLOAD & AGGREGATE PER TEAM ────────────────────────────────────────
def build_team_log(team):
    frames = []
    for year in YEARS:
        url = f"{BASE}/teams/{team}/{year}.htm"
        print(f"[{team.upper()}] fetching GameLog {year} …")
        r = fetch_url(url)
        if not r:
            continue
        soup = BeautifulSoup(r.text, "html.parser")
        tbl = soup.find("table", {"data-soc-sum-table-type": "TeamGamelog"})
        if not tbl:
            print(f"   no GameLog table for {year}")
            continue
        df = pd.read_html(str(tbl), header=[0,1])[0]
        df = flatten_multiindex(df)
        df.insert(0, "Year", year)
        frames.append(df)
        time.sleep(random.uniform(4, 5))
    if not frames:
        print(f"No data for team {team}, skipping.")
        return
    full = pd.concat(frames, ignore_index=True, sort=False)
    out_path = os.path.join(OUT_DIR, f"{team}_2006_2024_gamelog.csv")
    full.to_csv(out_path, index=False)
    print(f"[{team.upper()}] saved → {out_path}")

def main():
    for team in TEAMS:
        build_team_log(team)

if __name__ == "__main__":
    main()
