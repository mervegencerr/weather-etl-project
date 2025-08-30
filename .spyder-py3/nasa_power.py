# -*- coding: utf-8 -*-


import requests
import os
from datetime import date, timedelta

output_dir = "data/raw/nasa_power/"
os.makedirs(output_dir, exist_ok = True)

base_url = "https://power.larc.nasa.gov/api/temporal/hourly/point"

# end_date = date.today()
end_date = date(2024, 6, 30)
start_date = end_date - timedelta(days = 29)
  
params = {
#   "latitude" : 43.6532,
#   "longitude" : -79.3832,
   "latitude" : 43.68,
   "longitude" : -79.63,
   "start" : start_date.strftime("%Y%m%d"),
   "end" : end_date.strftime("%Y%m%d"),
   "parameters" : "ALLSKY_SFC_SW_DWN,ALLSKY_SFC_SW_DNI,ALLSKY_SFC_SW_DIFF,T2M,WS10M",
   "community" : "RE",
   "format" : "JSON",
   "time-standard" : "UTC"
   }
    
response = requests.get(base_url, params = params, timeout = 60)
fname = "nasa_power.json"
fpath = os.path.join(output_dir, fname)
with open(fpath, "w", encoding="utf-8") as f:
    f.write(response.text)

