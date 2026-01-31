import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
from pathlib import Path

URL = "https://www.spotrac.com/nfl/rankings/player/_/year/2025/sort/cap_total"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; nfl-project/1.0)"
}

OUTPUT_PATH = Path("base-data/data/player-cap.json")


def fetch_spotrac_2025_cap():
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    table = soup.find("table")

    if table is None:
        raise ValueError("Spotrac table not found")

    rows = table.find("tbody").find_all("tr")
    players = []

    for row in rows:
        cols = [c.get_text(strip=True) for c in row.find_all("td")]

        if len(cols) < 8:
            continue

        players.append({
            "player": cols[1],
            "team": cols[2],
            "position": cols[3],
            "age": int(cols[4]) if cols[4].isdigit() else None,
            "cap_hit": float(cols[5].replace("$", "").replace(",", "")),
            "cash_2025": float(cols[6].replace("$", "").replace(",", "")),
            "contract_length": cols[7],
            "season": 2025
        })

    return players


if __name__ == "__main__":
    data = fetch_spotrac_2025_cap()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_PATH, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Saved {OUTPUT_PATH}")
