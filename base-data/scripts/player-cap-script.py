import requests
import pandas as pd
from bs4 import BeautifulSoup
import time

URL = "https://www.spotrac.com/nfl/rankings/player/_/year/2025/sort/cap_total"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; TangentWiseBot/1.0; +https://tangentwise.com)"
}

def fetch_spotrac_2025_cap():
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    table = soup.find("table")
    if table is None:
        raise ValueError("Could not find data table on Spotrac page")

    rows = table.find("tbody").find_all("tr")

    data = []

    for row in rows:
        cols = [c.get_text(strip=True) for c in row.find_all("td")]

        if len(cols) < 8:
            continue

        data.append({
            "player": cols[1],
            "team": cols[2],
            "position": cols[3],
            "age": cols[4],
            "cap_hit": cols[5],
            "cash_2025": cols[6],
            "contract_length": cols[7],
        })

    df = pd.DataFrame(data)

    # Clean money columns
    money_cols = ["cap_hit", "cash_2025"]
    for col in money_cols:
        df[col] = (
            df[col]
            .str.replace("$", "", regex=False)
            .str.replace(",", "", regex=False)
            .astype(float)
        )

    return df


if __name__ == "__main__":
    df = fetch_spotrac_2025_cap()

    df.to_csv("nfl_2025_cap_hit.csv", index=False)

    print("Saved nfl_2025_cap_hit.csv")
    print(df.head())
