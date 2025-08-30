# -*- coding: utf-8 -*-

import os
import json
import pandas as pd
from pathlib import Path

# step1 : quality check for eccc

def quality_check_csv(filepath : Path, required_columns = None) : 
    problems = []
    
    if not filepath.exists() or filepath.stat().st_size == 0 : 
        problems.append("File is empty.")
        return
    
    df = pd.read_csv(filepath)
    
    if required_columns : 
        missing_columns = [column for column in required_columns if column not in df.columns]
        if missing_columns : 
            problems.append(f"Missing columns : {missing_columns}")
    
    timestamp = None
    if "Date/Time (LST)" in df.columns : 
        timestamp = pd.to_datetime(df["Date/Time (LST)"], errors = "coerce")
    
    if timestamp is None : 
        problems.append("Timestamp could not be derived.")
        
    
eccc_required = ["Date/Time (LST)", "Longitude (x)", "Latitude (y)", "Temp (°C)", "Wind Spd (km/h)"]
quality_check_csv(Path("data/raw/eccc/20250730.csv"), required_columns = eccc_required)

