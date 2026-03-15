"""
check_csv.py
Run this in the same folder as your combined_rainfall.csv
It will show you exactly what pandas sees — date format, columns, row count etc.

Run with:  python check_csv.py
"""

import pandas as pd
import os

csv_file = 'combined_rainfall.csv'

print("=" * 60)
print("  CSV DIAGNOSTIC TOOL")
print("=" * 60)

# ── 1. Does the file exist? ───────────────────────────────────
if not os.path.exists(csv_file):
    print(f"\n✗ File not found: {csv_file}")
    print(f"  Current folder is: {os.getcwd()}")
    print(f"  Files here: {os.listdir('.')}")
    exit()

file_size = os.path.getsize(csv_file) / 1024
print(f"\n✓ File found: {csv_file}  ({file_size:.0f} KB)")

# ── 2. Read raw — no parsing ──────────────────────────────────
print("\n[1] Reading raw (no date parsing)...")
df_raw = pd.read_csv(csv_file, nrows=10)
print(f"\n  Column names: {list(df_raw.columns)}")
print(f"\n  First 10 rows (raw):")
print(df_raw.to_string(index=False))

# ── 3. Show date column values ────────────────────────────────
print(f"\n[2] Checking date column format...")
df_dates = pd.read_csv(csv_file, usecols=['date'], nrows=20)
print(f"\n  First 20 date values:")
for i, v in enumerate(df_dates['date'].values):
    print(f"    [{i+1:02d}] {repr(v)}")

# ── 4. Try different date parsings ───────────────────────────
print(f"\n[3] Trying date parsing methods...")

# Method A — default
try:
    df_a = pd.read_csv(csv_file, parse_dates=['date'], nrows=5)
    print(f"\n  Method A (default):       {df_a['date'].iloc[0]}  → dtype: {df_a['date'].dtype}")
except Exception as e:
    print(f"\n  Method A failed: {e}")

# Method B — dayfirst
try:
    df_b = pd.read_csv(csv_file, parse_dates=['date'], dayfirst=True, nrows=5)
    print(f"  Method B (dayfirst=True): {df_b['date'].iloc[0]}  → dtype: {df_b['date'].dtype}")
except Exception as e:
    print(f"  Method B failed: {e}")

# Method C — manual format DD/MM/YYYY
try:
    df_c = pd.read_csv(csv_file, nrows=5)
    df_c['date'] = pd.to_datetime(df_c['date'], format='%d/%m/%Y')
    print(f"  Method C (DD/MM/YYYY):    {df_c['date'].iloc[0]}  → dtype: {df_c['date'].dtype}")
except Exception as e:
    print(f"  Method C (DD/MM/YYYY) failed: {e}")

# Method D — manual format YYYY-MM-DD
try:
    df_d = pd.read_csv(csv_file, nrows=5)
    df_d['date'] = pd.to_datetime(df_d['date'], format='%Y-%m-%d')
    print(f"  Method D (YYYY-MM-DD):    {df_d['date'].iloc[0]}  → dtype: {df_d['date'].dtype}")
except Exception as e:
    print(f"  Method D (YYYY-MM-DD) failed: {e}")

# Method E — infer format
try:
    df_e = pd.read_csv(csv_file, nrows=5)
    df_e['date'] = pd.to_datetime(df_e['date'], infer_datetime_format=True)
    print(f"  Method E (infer format):  {df_e['date'].iloc[0]}  → dtype: {df_e['date'].dtype}")
except Exception as e:
    print(f"  Method E (infer) failed: {e}")

# ── 5. Full file stats ────────────────────────────────────────
print(f"\n[4] Full file stats...")
df_full = pd.read_csv(csv_file)
print(f"\n  Total rows:    {len(df_full):,}")
print(f"  Columns:       {list(df_full.columns)}")
print(f"  Station values: {df_full['station'].unique()}")
print(f"  Rain column:   min={df_full['rain'].min()}, max={df_full['rain'].max()}, nulls={df_full['rain'].isna().sum()}")
print(f"\n  First date value (raw): {repr(df_full['date'].iloc[0])}")
print(f"  Last  date value (raw): {repr(df_full['date'].iloc[-1])}")

print(f"\n{'='*60}")
print("  Copy the output above and share it — that tells us exactly")
print("  what format your dates are in so we can fix the loader.")
print(f"{'='*60}\n")
