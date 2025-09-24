#!/usr/bin/env python3
import os
import time
import random
import requests
import pandas as pd
from bs4 import BeautifulSoup, Comment

# ─── CONFIG ────────────────────────────────────────────────────────────────
BASE_URL    = "https://www.pro-football-reference.com/teams/{team}/{year}_roster.htm"
TEAMS       = [
    'crd','atl','rav','buf','car','chi','cin','cle','dal','den','det',
    'gnb','htx','clt','jax','kan','sdg','ram','rai','mia','min','nwe',
    'nor','nyg','nyj','phi','pit','sea','sfo','tam','oti','was'
]
YEARS       = range(2006, 2025)
HEADERS     = {"User-Agent": "Mozilla/5.0"}
OUTPUT_DIR  = "team_roster2"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─── HELPERS ───────────────────────────────────────────────────────────────
def fetch_page(url, timeout=10):
    try:
        return requests.get(url, headers=HEADERS, timeout=timeout)
    except requests.RequestException:
        return None

def all_tables(soup):
    """Return all <table> tags, including those inside HTML comments."""
    tables = soup.find_all("table")
    for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
        if "<table" in comment:
            comment_soup = BeautifulSoup(comment, "html.parser")
            tables.extend(comment_soup.find_all("table"))
    return tables

# ─── MAIN SCRAPER ──────────────────────────────────────────────────────────
for year in YEARS:
    year_frames = []
    print(f"=== Processing season {year} ===")

    for team in TEAMS:
        # polite pause before each request
        wait = random.uniform(4, 5)
        print(f"[{team.upper()} {year}] sleeping {wait:.2f}s…")
        time.sleep(wait)

        url = BASE_URL.format(team=team, year=year)
        print(f"[{team.upper()} {year}] fetching {url}")
        resp = fetch_page(url)
        if not resp or resp.status_code != 200:
            print(f"   ⚠️ skipped (status {getattr(resp, 'status_code', 'ERR')})")
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        tables = all_tables(soup)
        if not tables:
            print("   ❌ no tables found, skipping")
            continue

        # take the last table
        tbl = tables[-1]
        try:
            df = pd.read_html(str(tbl))[0]
        except ValueError as e:
            print(f"   ❌ parse error: {e}")
            continue

        # annotate and collect
        df.insert(0, "Team", team.upper())
        df.insert(1, "Year", year)
        year_frames.append(df)
        print("   ✅ table parsed")

    # combine and save one CSV per year
    if year_frames:
        combined = pd.concat(year_frames, ignore_index=True, sort=False)
        out_path = os.path.join(OUTPUT_DIR, f"{year}_team_rosters.csv")
        combined.to_csv(out_path, index=False)
        print(f"✅ Wrote season file → {out_path}")
    else:
        print(f"⚠️ No data for {year}, skipping CSV write")

print("🎉 All done — one CSV per year in `team_roster2/`.")
