import requests
import pandas as pd

# Create a session and set a realistic User-Agent to avoid ESPN’s 403 block
session = requests.Session()
session.headers.update({
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/114.0.0.0 Safari/537.36'
    )
})

url = "https://www.espn.com/nfl/schedulegrid"
resp = session.get(url)
resp.raise_for_status()

# Parse the first HTML table on the page into a DataFrame
dfs = pd.read_html(resp.text)
if not dfs:
    raise RuntimeError("No tables found on schedulegrid page")

schedule_df = dfs[0]

# Save to CSV
schedule_df.to_csv("nfl_schedulegrid.csv", index=False)
print(f"Saved schedule grid ({schedule_df.shape[0]} rows × {schedule_df.shape[1]} cols) to nfl_schedulegrid.csv")
