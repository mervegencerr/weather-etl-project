# -*- coding: utf-8 -*-

import sqlite3
import pandas as pd
from pathlib import Path

con = sqlite3.connect("weather.db") 
cursor = con.cursor()

cursor.execute("""
CREATE TABLE stg_eccc_hourly (

  timestamp_utc TEXT
  , latitude REAL 
  , longitude REAL 
  , air_temp_c REAL
  , wind_speed_kmh REAL

)""")

input_dir = Path("data/clean")
for csv_file in input_dir.glob("*_clean.csv"):
    df = pd.read_csv(csv_file)

    df.to_sql("stg_eccc_hourly", con, if_exists="append", index=False)
    
    
input_dir = Path("data/clean/nasa_powerclean.csv")
with open(input_dir, "r") as f:
    df = pd.read_csv(f) 
 
df.to_sql("stg_nasa_power_hourly", con, if_exists="append", index=False)
    
con.close()
    


