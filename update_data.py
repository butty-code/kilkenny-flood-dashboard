"""
update_data.py
──────────────────────────────────────────────────────────────
Met Éireann Live Data Updater
Downloads the latest daily rainfall data directly from Met Éireann's
open data portal and appends it to your combined_rainfall.csv

HOW IT WORKS:
  Met Éireann publishes every station's data as a downloadable CSV at:
  https://cli.fusio.net/cli/climate_data/webdata/dly{STATION_NO}.csv

  Station numbers for our two stations:
    • Kilkenny (Lavistown):        3923
    • Graiguenamanagh (Ballyogan): 4175

  The script:
    1. Downloads the full CSV for each station from Met Éireann
    2. Parses rainfall (rain column) and date
    3. Finds any dates not already in your combined_rainfall.csv
    4. Appends only the new rows
    5. Saves the updated file — ready for the dashboard

HOW TO RUN:
  python update_data.py

HOW TO AUTOMATE (Windows):
  Use Windows Task Scheduler to run this once a day:
    1. Open Task Scheduler → Create Basic Task
    2. Name: "Met Éireann Rainfall Update"
    3. Trigger: Daily, at 08:00
    4. Action: Start a program → python
    5. Arguments: C:/kilkenny_flood_dashboard/update_data.py
    6. Start in: C:/kilkenny_flood_dashboard
──────────────────────────────────────────────────────────────
"""

import pandas as pd
import numpy as np
import requests
import os
from datetime import datetime
from io import StringIO

# ── Configuration ────────────────────────────────────────────
CSV_FILE   = 'combined_rainfall.csv'
LOG_FILE   = 'update_log.txt'

STATIONS = {
    'Kilkenny':        3923,   # Lavistown House
    'Graiguenamanagh': 4175,   # Ballyogan House
}

BASE_URL = 'https://cli.fusio.net/cli/climate_data/webdata/dly{}.csv'

# ── Logging helper ───────────────────────────────────────────
def log(msg):
    ts  = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{ts}] {msg}'
    print(line)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')


# ── Download one station from Met Éireann ────────────────────
def fetch_station(station_name, station_no):
    url = BASE_URL.format(station_no)
    log(f'Fetching {station_name} (station {station_no}) from Met Éireann...')
    log(f'  URL: {url}')

    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        log(f'  ✗ Download failed: {e}')
        return None

    raw = resp.text
    log(f'  ✓ Downloaded {len(raw):,} bytes')

    # Met Éireann CSV files have metadata header rows before the actual data
    # Find the line that contains 'date' as the first column header
    lines = raw.splitlines()
    header_idx = None
    for i, line in enumerate(lines):
        if line.lower().startswith('date'):
            header_idx = i
            break

    if header_idx is None:
        log(f'  ✗ Could not find data header row in {station_name} CSV')
        log(f'  First 10 lines: {lines[:10]}')
        return None

    log(f'  → Data starts at line {header_idx + 1}')

    # Parse from the header row onwards
    data_str = '\n'.join(lines[header_idx:])
    try:
        df = pd.read_csv(StringIO(data_str), low_memory=False)
    except Exception as e:
        log(f'  ✗ CSV parse failed: {e}')
        return None

    log(f'  → Columns: {list(df.columns)}')
    log(f'  → Raw rows: {len(df):,}')

    # Standardise column names to lowercase
    df.columns = [c.strip().lower() for c in df.columns]

    # We need: date and rain
    if 'date' not in df.columns:
        log(f'  ✗ No "date" column found. Columns: {list(df.columns)}')
        return None

    if 'rain' not in df.columns:
        # Try common alternatives
        for alt in ['rainfall', 'precip', 'precipitation', 'rain(mm)', 'rain (mm)']:
            if alt in df.columns:
                df = df.rename(columns={alt: 'rain'})
                log(f'  → Renamed "{alt}" → "rain"')
                break
        if 'rain' not in df.columns:
            log(f'  ✗ No rainfall column found. Columns: {list(df.columns)}')
            return None

    # Parse dates
    df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['date'])

    # Clean rainfall values
    df['rain'] = pd.to_numeric(df['rain'], errors='coerce').fillna(0).clip(lower=0)

    # Get ind column if present, otherwise default to 1
    if 'ind' not in df.columns:
        df['ind'] = 1
    else:
        df['ind'] = pd.to_numeric(df['ind'], errors='coerce').fillna(1)

    # Keep only what we need
    df = df[['date', 'ind', 'rain']].copy()
    df['station'] = station_name
    df = df.sort_values('date').reset_index(drop=True)

    log(f'  ✓ Parsed {len(df):,} records: '
        f'{df["date"].min().date()} → {df["date"].max().date()}')
    return df


# ── Load existing CSV ─────────────────────────────────────────
def load_existing():
    if not os.path.exists(CSV_FILE):
        log(f'  No existing {CSV_FILE} found — will create fresh')
        return pd.DataFrame(columns=['date', 'ind', 'rain', 'station'])

    df = pd.read_csv(CSV_FILE)
    df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['date'])
    log(f'  Existing file: {len(df):,} rows, '
        f'{df["date"].min().date()} → {df["date"].max().date()}')
    return df


# ── Main update logic ─────────────────────────────────────────
def update():
    log('=' * 55)
    log('  MET ÉIREANN DATA UPDATE')
    log(f'  Run date: {datetime.now().strftime("%A %d %B %Y %H:%M")}')
    log('=' * 55)

    existing = load_existing()
    all_new_rows = []
    total_added  = 0

    for station_name, station_no in STATIONS.items():
        log(f'\n── {station_name} ────────────────────────────')

        fresh = fetch_station(station_name, station_no)
        if fresh is None:
            log(f'  ✗ Skipping {station_name} — download or parse failed')
            continue

        # Find dates not in existing data for this station
        existing_station = existing[existing['station'] == station_name]
        existing_dates   = set(existing_station['date'].dt.date)
        fresh_dates      = set(fresh['date'].dt.date)

        new_dates   = fresh_dates - existing_dates
        new_rows_df = fresh[fresh['date'].dt.date.isin(new_dates)]

        if len(new_rows_df) == 0:
            log(f'  ✓ {station_name} — already up to date, no new rows')
        else:
            log(f'  + {len(new_rows_df):,} new rows to add '
                f'({min(new_dates)} → {max(new_dates)})')
            all_new_rows.append(new_rows_df)
            total_added += len(new_rows_df)

        # Also check for any updated values (ind flag changes)
        common_dates = fresh_dates & existing_dates
        if common_dates:
            fresh_common    = fresh[fresh['date'].dt.date.isin(common_dates)]
            existing_common = existing_station[
                existing_station['date'].dt.date.isin(common_dates)]
            # Check if any rain values changed
            merged = fresh_common.merge(
                existing_common[['date', 'rain']],
                on='date', suffixes=('_new', '_old')
            )
            changed = merged[
                abs(merged['rain_new'] - merged['rain_old']) > 0.05
            ]
            if len(changed) > 0:
                log(f'  ~ {len(changed)} existing values were updated '
                    f'(quality control revisions from Met Éireann)')

    # Save updated file
    if total_added > 0:
        log(f'\n── Saving updated CSV ───────────────────────')
        combined = pd.concat([existing] + all_new_rows, ignore_index=True)
        combined = combined.sort_values(['station', 'date']).reset_index(drop=True)

        # Format date back to the original DD-Mon-YY format your file uses
        combined['date'] = combined['date'].dt.strftime('%d-%b-%y')

        combined.to_csv(CSV_FILE, index=False)
        log(f'  ✓ Saved {len(combined):,} total rows to {CSV_FILE}')
        log(f'  ✓ Added {total_added:,} new rows total')
    else:
        log(f'\n  ✓ No updates needed — data is already current')

    log(f'\n  Done. Next run: tomorrow at 08:00')
    log('=' * 55 + '\n')
    return total_added


# ── Entry point ───────────────────────────────────────────────
if __name__ == '__main__':
    update()
