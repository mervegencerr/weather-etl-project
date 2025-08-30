# Buluttan Weather ETL (Case Study)

Small end‑to‑end ETL that fetches hourly **weather** (ECCC) and **solar radiation** (NASA POWER), performs QC + cleaning, loads to **SQLite**, builds a unified fact table, and answers analytical questions with SQL.

> ⚠️ Notes
>
> * The original ECCC **stationID** (26953) returned no data; the pipeline continues with a working **stationID**.
> * NASA POWER returned no data for the last 30 days; therefore the **date range** was adjusted.
> * Some quality checks and quarantining steps (Part 2) were partially implemented.

---

## Repository Structure

```
.
├── data/
│   ├── raw/
│   │   ├── eccc/
│   │   └── nasa_power/
│   ├── clean/
│   └── quarantine/
├── src/
│   └── transform.py
├── transform.sql
├── report.sql
├── answers.csv
└── weather.db
```

---

## Quickstart

### Requirements

* Python 3.10+
* sqlite3

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Steps

1. **Fetch Data** (raw CSV/JSON into `data/raw/`).
2. **Clean & Load** (normalize timestamps, rename columns, write to `data/clean/`, load staging tables in `weather.db`).
3. **Transform**:

   ```bash
   sqlite3 weather.db < transform.sql
   ```

   → builds `final_weather_report`.
4. **Report**:

   ```bash
   sqlite3 -header -csv weather.db < report.sql > answers.csv
   ```

---

## Data Sources

### ECCC – Hourly Climate Data

CSV endpoint template:

```
https://climate.weather.gc.ca/climate_data/bulk_data_e.html?
format=csv&stationID=<STATION_ID>&Year=<YYYY>&Month=<M>&Day=<D>&
time=LST&timeframe=1&submit=Download+Data
```

### NASA POWER – Hourly Solar & Met Data

JSON endpoint:

```
https://power.larc.nasa.gov/api/temporal/hourly/point
```

Parameters: `latitude`, `longitude`, `start`, `end`, `parameters`, `community=RE`, `format=JSON`, `time-standard=UTC`.

Join key: `(latitude, longitude, timestamp_utc)`.

---

## Data Quality Checks

* Non-empty files
* Expected columns present
* Valid timestamps (ISO8601, hourly continuity)
* Duplicate key checks `(latitude, longitude, timestamp_utc)`

> Quarantine and logging steps are not fully automated.

---

## Cleaning & Column Standards

* All timestamps converted to **UTC** → `timestamp_utc`
* Column names standardized to `snake_case`
* Kept fields:

  * **ECCC:** `timestamp_utc`, `latitude`, `longitude`, `air_temp_c`, `wind_speed_kmh`
  * **NASA:** `timestamp_utc`, `latitude`, `longitude`, `ghi_wm2`, `dni_wm2`, `dif_wm2`

---

## Database Schema (SQLite)

### Staging Tables

* **stg\_eccc\_hourly**
* **stg\_nasa\_power\_hourly**

### Final Table: `final_weather_report`

* Join: `(latitude, longitude, timestamp_utc)`
* Derived fields:

  * `temp_anomaly_c`
  * `wind_flag_high`
  * `solar_score`

---

## Analytical Queries (report.sql)

1. Highest average `solar_score` day
2. Highest total GHI (daily)
3. Hour of day with most `wind_flag_high`
4. Correlation between `air_temp_c` and `ghi_wm2`
5. Top 5 largest absolute `temp_anomaly_c` values

---

## Workflow Summary

1. Download → `data/raw/`
2. Clean → `data/clean/`
3. Load → `weather.db`
4. Transform → `transform.sql`
5. Report → `report.sql` → `answers.csv`

---

## Assumptions & Issues

* Original station ID invalid → replaced
* NASA POWER recent window empty → adjusted dates
* ECCC LST normalized to UTC
* QC partial automation only

---

## Column Definitions

* `timestamp_utc` – ISO8601 UTC hour
* `latitude`, `longitude` – decimal degrees
* `air_temp_c` – °C
* `wind_speed_kmh` – km/h
* `ghi_wm2`, `dni_wm2`, `dif_wm2` – W/m²
* `temp_anomaly_c` – deviation from 30-day mean
* `wind_flag_high` – 1 if wind ≥ 50 km/h
* `solar_score` – (GHI + DNI) / 2

---

## Limitations & Improvements

* Retry strategies for API errors
* Automated QC & quarantine with logs
* Gap-filling for missing hours
* Coordinate-tolerant joins
* Docker/Makefile automation

---

## License

Technical assessment only.
