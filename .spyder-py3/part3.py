# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os
import json
from pathlib import Path
from dateutil import tz

input_dir = Path("data/raw/eccc/")
output_dir = "data/clean"
os.makedirs(output_dir, exist_ok = True)

local_timezone = tz.gettz("America/Toronto")

for csv_file in input_dir.glob("*.csv"):
    df = pd.read_csv(csv_file)
    
    date_column = df["Date/Time (LST)"]
    date_column = pd.to_datetime(date_column, errors = "coerce")
    date_column = date_column.dt.tz_localize(local_timezone, ambiguous="NaT", nonexistent="NaT")
    
    timestamp_utc = date_column.dt.tz_convert("UTC")
    
    eccc_df = pd.DataFrame({
        "timestamp_utc" : timestamp_utc,
        "latitude" : df.get("Latitude (y)", np.nan),
        "longitude" : df.get("Longitude (x)", np.nan),
        "air_temp_c" : df.get("Temp (°C)", np.nan),
        "wind_speed_kmh" : df.get("Wind Spd (km/h)", np.nan)
        })
    
    fname = f"{csv_file.stem}_clean.csv"
    output_path = os.path.join(output_dir, fname)
    eccc_df.to_csv(output_path, index = False)
    
    
input_dir = Path("data/raw/nasa_power/nasa_power.json")

with open(input_dir, "r") as f:
    nasa_power_data = json.load(f) 
    
latitude = nasa_power_data["geometry"]["coordinates"][1]
longitude = nasa_power_data["geometry"]["coordinates"][0]

parameters = nasa_power_data["properties"]["parameter"]

def get_values(key) :
    values = pd.Series(parameters.get(key, {}), dtype="float64")
    values.replace(-999.0, np.nan, inplace = True)
    nasa_timestamp_utc = pd.to_datetime(values.index, format = "%Y%m%d%H", utc = True, errors = "coerce")
    values.index = nasa_timestamp_utc
    values.name = key
    return values

ghi = get_values("ALLSKY_SFC_SW_DWN")   # global horizontal irradiance
dni = get_values("ALLSKY_SFC_SW_DNI")   # direct normal irradiance
dif = get_values("ALLSKY_SFC_SW_DIFF")  # diffuse horizontal irradiance

nasa_df = pd.concat([ghi, dni, dif], axis = 1).sort_index()

nasa_df.rename(columns = {
    "ALLSKY_SFC_SW_DWN": "ghi_wm2",
    "ALLSKY_SFC_SW_DNI": "dni_wm2",
    "ALLSKY_SFC_SW_DIFF": "dif_wm2",
}, inplace = True)

nasa_df["latitude"] = latitude
nasa_df["longitude"] = longitude

# indexi kolona çevir
nasa_df.reset_index(inplace = True)
nasa_df.rename(columns={"index": "timestamp_utc"}, inplace = True)

# kolon sırası
nasa_df = nasa_df[["timestamp_utc", "latitude", "longitude", "ghi_wm2", "dni_wm2", "dif_wm2"]]

fname = "nasa_powerclean.csv"
output_path = os.path.join(output_dir, fname)
nasa_df.to_csv(output_path, index = False)