# -*- coding: utf-8 -*-
# qc_part2_csv_json.py
from pathlib import Path
import os, json
import pandas as pd

# ==== AYARLAR ====
CSV_DIR = Path("data/eccc_csvs")                   # 30 CSV'nin olduğu klasör
JSON_PATH = Path("data/raw/nasa_power/nasa_power.json")           # tek JSON dosyan
QC_THRESHOLD = 0.90
CSV_REQUIRED_COLS = ["Date/Time (LST)", "Longitude (x)", "Latitude (y)", "Temp (°C)", "Wind Spd (km/h)"]

JSON_REQUIRED_PARAMS = [                          # JSON içindeki parameter anahtarları
    "ALLSKY_SFC_SW_DWN", "ALLSKY_SFC_SW_DNI",
    "ALLSKY_SFC_SW_DIFF", "T2M", "WS10M"
]
TIMESTAMP_SINGLE_COL = "Date/Time (LST)"          # varsa önce bunu kullan

# ==== YARDIMCILAR ====
def derive_timestamp_csv(df: pd.DataFrame) -> pd.Series | None:
    if TIMESTAMP_SINGLE_COL in df.columns:
        return pd.to_datetime(df[TIMESTAMP_SINGLE_COL], errors="coerce")
    if {"Year","Month","Day"}.issubset(df.columns):
        time_cols = [c for c in df.columns if "time" in c.lower()]
        if time_cols:
            tcol = time_cols[0]
            s = (
                df["Year"].astype(str).str.zfill(4) + "-" +
                df["Month"].astype(str).str.zfill(2) + "-" +
                df["Day"].astype(str).str.zfill(2) + " " +
                df[tcol].astype(str)
            )
            return pd.to_datetime(s, errors="coerce")
    return None

def find_lat_lon_cols(df: pd.DataFrame):
    lat = next((c for c in df.columns if "lat" in c.lower()), None)
    lon = next((c for c in df.columns if "lon" in c.lower()), None)
    return lat, lon

# ==== CSV KÜMESİ (GLOBAL) QC ====
def qc_csv_folder(csv_dir: Path, required_cols: list[str]):
    files = sorted(csv_dir.glob("*.csv"))
    if not files:
        print(f"[CSV] No CSV files in {csv_dir}")
        return {"files":0, "total_rows":0, "valid_ts":0, "ratio":0.0, "global_dups":0, "problems":["No CSV files"]}

    total_rows = 0
    total_valid = 0
    all_keys = []
    problems = []
    file_count = 0

    for p in files:
        if p.stat().st_size == 0:
            problems.append(f"{p.name}: file is empty")
            continue
        try:
            df = pd.read_csv(p)
        except Exception as e:
            problems.append(f"{p.name}: read error -> {e}")
            continue

        file_count += 1
        # required columns per file
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            problems.append(f"{p.name}: missing columns {missing}")

        ts = derive_timestamp_csv(df)
        lat_col, lon_col = find_lat_lon_cols(df)

        total_rows += len(df)
        if ts is not None:
            total_valid += ts.notna().sum()
            if lat_col and lon_col:
                all_keys.append(pd.DataFrame({"lat": df[lat_col], "lon": df[lon_col], "ts": ts}))
        # ts None ise oran hesabında sadece satır artar, valid artmaz (doğru davranış)

    ratio = (total_valid / total_rows) if total_rows else 0.0
    if all_keys:
        keys = pd.concat(all_keys, ignore_index=True).dropna(subset=["ts"])
        global_dups = int(keys.duplicated(["lat","lon","ts"]).sum())
    else:
        global_dups = 0

    # PASS/FAIL mesajları
    print("\n=== CSV (ALL FILES TOGETHER) ===")
    print(f"files read: {file_count}/{len(files)}")
    print(f"total rows: {total_rows}")
    print(f"valid timestamps: {total_valid}")
    print(f"overall valid ratio: {ratio:.1%}  -> {'PASS ✅' if ratio >= QC_THRESHOLD else 'FAIL ❌'}")
    print(f"global duplicates (lat,lon,ts): {global_dups}")
    if problems:
        print("notes/problems:")
        for msg in problems: print(" -", msg)

    return {"files":file_count, "total_rows":total_rows, "valid_ts":total_valid,
            "ratio":ratio, "global_dups":global_dups, "problems":problems}

# ==== JSON TEK DOSYA QC ====
def qc_single_json(json_path: Path, required_params: list[str]):
    problems = []
    if not json_path.exists() or json_path.stat().st_size == 0:
        print("\n=== JSON ===")
        print(f"{json_path.name}: file missing or empty -> FAIL ❌")
        return {"rows":0, "valid_ts":0, "ratio":0.0, "dups":0, "problems":["missing/empty"]}

    try:
        data = json.load(open(json_path, "r"))
    except Exception as e:
        print("\n=== JSON ===")
        print(f"read error -> {e}")
        return {"rows":0, "valid_ts":0, "ratio":0.0, "dups":0, "problems":[f"read error: {e}"]}

    # required parameter keys
    params = data.get("properties", {}).get("parameter", {})
    miss = [k for k in required_params if k not in params]
    if miss:
        problems.append(f"missing parameters: {miss}")

    # timestamps are the dict keys like 'YYYYMMDDHH' across all parameters
    keys = sorted({k for d in params.values() if isinstance(d, dict) for k in d.keys()})
    ts = pd.to_datetime(pd.Series(keys), format="%Y%m%d%H", errors="coerce")
    rows = len(ts)
    valid = int(ts.notna().sum())
    ratio = (valid / rows) if rows else 0.0
    dups = int(pd.Series(keys).duplicated().sum())

    print("\n=== JSON (SINGLE FILE) ===")
    print(f"timestamps total: {rows}")
    print(f"valid timestamps: {valid}")
    print(f"valid ratio: {ratio:.1%}  -> {'PASS ✅' if ratio >= QC_THRESHOLD else 'FAIL ❌'}")
    print(f"duplicate timestamps: {dups}")
    if problems:
        print("notes/problems:")
        for msg in problems: print(" -", msg)

    return {"rows":rows, "valid_ts":valid, "ratio":ratio, "dups":dups, "problems":problems}

# ==== ÇALIŞTIR ====
if __name__ == "__main__": 
    csv_summary = qc_csv_folder(CSV_DIR, CSV_REQUIRED_COLS)
    json_summary = qc_single_json(JSON_PATH, JSON_REQUIRED_PARAMS)