import pandas as pd
import json
from pathlib import Path

URL = "https://www.spotrac.com/nfl/rankings/player/_/year/2025/sort/cap_total"
OUTPUT_PATH = Path("base-data/data/player-cap.json")

def fetch_spotrac_2025_cap():
    # read_html handles Spotrac's markup correctly
    tables = pd.read_html(URL)

    if not tables:
        raise ValueError("No tables found on Spotrac page")

    df = tables[0]

    # Inspect expected columns defensively
    df.columns = [c.lower().replace(" ", "_") for c in df.columns]

    required_cols = [
        "player",
        "team",
        "pos",
        "age",
        "cap_hit",
        "cash",
        "yrs"
    ]

    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Expected column not found: {col}")

    df = df[required_cols].copy()

    # Clean numeric columns
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
    df["season"] = 2025

    # Rename for consistency
    df = df.rename(columns={
        "pos": "position",
        "cash": "cash_2025",
        "yrs": "contract_years"
    })

    return df.to_dict(orient="records")


if __name__ == "__main__":
    data = fetch_spotrac_2025_cap()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_PATH, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Saved {OUTPUT_PATH}")
