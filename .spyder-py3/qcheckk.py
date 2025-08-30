# -*- coding: utf-8 -*-


import os
import json
import pandas as pd
from pathlib import Path

# === QC Fonksiyonları ===
def qc_eccc_csv(file_path: Path):
    problems = []

    if not file_path.exists() or file_path.stat().st_size == 0:
        print(f"{file_path.name}: ❌ File missing or empty")
        return

    df = pd.read_csv(file_path)

    # Latitude / Longitude kolonlarını bul
    lat_col = next((c for c in df.columns if "lat" in c.lower()), None)
    lon_col = next((c for c in df.columns if "lon" in c.lower()), None)

    # Timestamp türet
    ts = None
    if "Date/Time (LST)" in df.columns:
        ts = pd.to_datetime(df["Date/Time (LST)"], errors="coerce")
    elif {"Year","Month","Day"}.issubset(df.columns) and any("time" in c.lower() for c in df.columns):
        time_col = [c for c in df.columns if "time" in c.lower()][0]
        ts_str = (df["Year"].astype(str).str.zfill(4) + "-" +
                  df["Month"].astype(str).str.zfill(2) + "-" +
                  df["Day"].astype(str).str.zfill(2) + " " +
                  df[time_col].astype(str))
        ts = pd.to_datetime(ts_str, errors="coerce")

    # QC Kontrolleri
    if lat_col is None: problems.append("Latitude column not found.")
    if lon_col is None: problems.append("Longitude column not found.")
    if ts is None: problems.append("Timestamp could not be derived.")
    else:
        ratio = ts.notna().mean()
        if ratio < 0.9:
            problems.append(f"Valid timestamps below threshold: {ratio:.1%}")
        # Duplicate check
        if lat_col and lon_col:
            dup = pd.DataFrame({"lat": df[lat_col], "lon": df[lon_col], "ts": ts}) \
                    .duplicated().sum()
            if dup > 0:
                problems.append(f"{dup} duplicate (lat, lon, ts) rows.")

    if problems:
        print(f"{file_path.name}: ❌ QC Failed")
        for p in problems:
            print("   -", p)
    else:
        print(f"{file_path.name}: ✅ QC Passed")


def qc_nasa_json(file_path: Path):
    problems = []

    if not file_path.exists() or file_path.stat().st_size == 0:
        print(f"{file_path.name}: ❌ File missing or empty")
        return

    with open(file_path, "r") as f:
        data = json.load(f)

    # Lat/Lon
    try:
        lon, lat = data["geometry"]["coordinates"][:2]
    except Exception:
        lat = lon = None
        problems.append("No geometry.coordinates found.")

    # Timestamps
    params = data.get("properties", {}).get("parameter", {})
    keys = []
    for d in params.values():
        if isinstance(d, dict):
            keys.extend(d.keys())
    ts = pd.to_datetime(pd.Series(keys), format="%Y%m%d%H", errors="coerce")

    ratio = ts.notna().mean() if len(ts) else 0
    if ratio < 0.9:
        problems.append(f"Valid timestamps below threshold: {ratio:.1%}")

    dup = pd.Series(keys).duplicated().sum()
    if dup > 0:
        problems.append(f"{dup} duplicate timestamp keys.")

    if problems:
        print(f"{file_path.name}: ❌ QC Failed")
        for p in problems:
            print("   -", p)
    else:
        print(f"{file_path.name}: ✅ QC Passed")


# === Kullanım ===
qc_eccc_csv(Path("eccc_51459_2025-07-29.csv"))
qc_nasa_json(Path("nasa_power_43.633_-79.396_2025-07-29_2025-08-27.json"))

