# -*- coding: utf-8 -*-

import requests
import os
from datetime import date, timedelta

output_dir = "data/raw/eccc/"                 # linux'da \
os.makedirs(output_dir, exist_ok = True)

base_url = "https://climate.weather.gc.ca/climate_data/bulk_data_e.html"

# end_date = date.today()
end_date = date(2024, 6, 30)
start_date = end_date - timedelta(days = 29)

for i in range((end_date - start_date).days + 1) : 
    temp_date = start_date + timedelta(days=i)
    
    params = {
    "format" : "csv",
#    "stationID" : 26953,
    "stationID" : 51459,
    "Year" : temp_date.year, 
    "Month" : temp_date.month,
    "Day" : temp_date.day,
    "time" : "LST",
    "timeframe" : 1,
    "submit" : "Download+Data"
    }
    
    response = requests.get(base_url, params = params, timeout = 60)
    fname = f"{temp_date.strftime('%Y%m%d')}.csv"
    fpath = os.path.join(output_dir, fname)
    with open(fpath, "w", encoding="utf-8") as f:
       f.write(response.text)
