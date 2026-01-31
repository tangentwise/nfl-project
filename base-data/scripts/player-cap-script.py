import requests
import pandas as pd
import json
from pathlib import Path
from io import StringIO

URL = "https://www.spotrac.com/nfl/rankings/player/_/year/2025/sort/cap_total"
OUTPUT_PATH = Path("base-data/data/player-cap.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.spotrac.com/"
}

def fetch_spotrac_2025_cap():
    response = requests.get(URL, headers=HEADERS, timeout=30)

    if response.status_code != 200:
        raise ValueError(f"Failed to fetch page: {response.status_code}")

    html = response.text

    tables = pd.read_html(StringIO(html))

    if not tables:
        raise ValueError("No tables found after HTML fetch")

    df = tables[0]

    # Normalize columns
    df.columns = [c.lower().replace(" ", "_") for c in df.columns]

    required_cols = ["player", "team", "pos", "age", "cap_hit", "cash", "yrs"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing expected column: {col}")

    df = df[required_cols].copy()

    # Clean numeric fields
    df["cap_hit"] = (
        df["cap_hit"]
        .astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .astype(float)
    )

    df["cash"] = (
        df["cash"]
        .astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .astype(float)
    )

    df["age"] = pd.to_numeric(df["age"], errors="coerce")

    df = df.rename(columns={
        "pos": "position",
        "cash": "cash_2025",
        "yrs": "contract_years"
    })

    df["season"] = 2025

    return df.to_dict(orient="records")


if __name__ == "__main__":
    data = fetch_spotrac_2025_cap()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_PATH, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Saved {OUTPUT_PATH}")
