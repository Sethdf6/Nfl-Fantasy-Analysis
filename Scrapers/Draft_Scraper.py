import time
import random
import requests
import pandas as pd

def fetch_url(url: str) -> str:
    """GET with a simple retry loop; returns text or raises."""
    while True:
        r = requests.get(url)
        if r.status_code == 404:
            return None
        try:
            r.raise_for_status()
            return r.text
        except requests.exceptions.RequestException:
            time.sleep(4)

def scrape_draft_year(year: int) -> pd.DataFrame:
    """
    Fetches the PFR draft page for `year`, grabs the table with id="drafts",
    skips the first header row (header=1), and returns Rnd, Pick, Team, Player + Year.
    """
    url = f"https://www.pro-football-reference.com/years/{year}/draft.htm"
    print(f"Fetching {year}…", end=" ")

    # pandas will parse even commented-out tables if you give it the right `attrs` and header row
    try:
        df = pd.read_html(
            url,
            attrs={"id": "drafts"},
            header=1,            # skip the top “group” header row
            flavor="lxml"        # make sure we use a parser that handles comments
        )[0]
    except ValueError:
        raise RuntimeError(f"No draft table found for {year}")

    # keep just the columns you asked for
    df = df[['Rnd', 'Pick', 'Tm', 'Player']].copy()
    df.rename(columns={'Tm': 'Team'}, inplace=True)

    # add your year column
    df['Year'] = year

    print(f"found {len(df)} picks")
    return df

def main():
    all_years = []
    for yr in range(2013, 2026):
        df_yr = scrape_draft_year(yr)
        all_years.append(df_yr)

        # pause between 5–6 seconds
        delay = random.uniform(5, 6)
        print(f"  (sleeping {delay:.1f}s…)\n")
        time.sleep(delay)

    out = pd.concat(all_years, ignore_index=True)
    out.to_csv("drafts_2013_2025.csv", index=False)
    print("✅ Saved drafts_2013_2025.csv")

if __name__ == '__main__':
    main()
