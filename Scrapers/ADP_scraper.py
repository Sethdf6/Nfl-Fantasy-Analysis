import requests
import pandas as pd

def scrape_fp_mock_adp_for_year(year: int):
    """
    Scrapes the mock draft ADP table for a given year from FantasyPros
    and writes it to a CSV named '{year}_adp_mock.csv'.
    """
    url = f"https://www.fantasypros.com/nfl/adp/overall.php?year={year}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36"
        )
    }
    print(f"Fetching ADP mock for {year}…", end=" ")
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()

    tables = pd.read_html(resp.text)
    if not tables:
        raise RuntimeError(f"No tables found for year {year}")

    # Pick the largest table by row count
    df = max(tables, key=lambda t: t.shape[0])

    output_csv = f"{year}_adp_mock.csv"
    df.to_csv(output_csv, index=False)
    print(f"saved {df.shape[0]}×{df.shape[1]} to {output_csv}")

def main():
    for year in range(2006, 2013):  # 2013 through 2020 inclusive
        scrape_fp_mock_adp_for_year(year)

if __name__ == "__main__":
    main()
