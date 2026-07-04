"""
Pull daily historical weather data for Santo Domingo from the Open-Meteo
Historical Weather API and cache it locally as CSV.

Usage:
    python scripts/fetch_historical_data.py
    python scripts/fetch_historical_data.py --start 2015-01-01 --end 2025-12-31 --force
"""

import argparse
from pathlib import Path

import pandas as pd
import requests

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

# Santo Domingo, Dominican Republic
LATITUDE = 18.4861
LONGITUDE = -69.9312
TIMEZONE = "America/Santo_Domingo"

DAILY_VARS = [
    "temperature_2m_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    "relative_humidity_2m_mean",
    "surface_pressure_mean",
    "windspeed_10m_max",
    "precipitation_sum",
]

DEFAULT_START = "2015-01-01"
DEFAULT_END = "2024-12-31"

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_FILE = DATA_DIR / "santo_domingo_historical.csv"


def fetch_historical_weather(start_date: str, end_date: str) -> pd.DataFrame:
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "start_date": start_date,
        "end_date": end_date,
        "daily": ",".join(DAILY_VARS),
        "timezone": TIMEZONE,
    }

    response = requests.get(ARCHIVE_URL, params=params, timeout=60)
    response.raise_for_status()
    payload = response.json()

    daily = payload["daily"]
    df = pd.DataFrame(daily)
    df.rename(columns={"time": "date"}, inplace=True)
    df["date"] = pd.to_datetime(df["date"])
    return df


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default=DEFAULT_START, help="Start date YYYY-MM-DD")
    parser.add_argument("--end", default=DEFAULT_END, help="End date YYYY-MM-DD")
    parser.add_argument(
        "--force", action="store_true", help="Re-fetch even if cached CSV already exists"
    )
    args = parser.parse_args()

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if OUTPUT_FILE.exists() and not args.force:
        print(f"Cached file already exists at {OUTPUT_FILE} (use --force to re-fetch).")
        return

    print(f"Fetching Santo Domingo daily weather from {args.start} to {args.end}...")
    df = fetch_historical_weather(args.start, args.end)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved {len(df)} rows to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
