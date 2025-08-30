CREATE TABLE final_weather_report AS

SELECT
  e.timestamp_utc
  , e.latitude
  , e.longitude
  , e.air_temp_c
  , e.wind_speed_kmh
  , n.ghi_wm2
  , n.dni_wm2
  , n.dif_wm2
  , e.air_temp_c - (SELECT AVG(air_temp_c) FROM stg_eccc_hourly) AS temp_anomaly_c
  
  , CASE 
     WHEN e.wind_speed_kmh >= 50 THEN 1
     ELSE 0
   END AS wind_flag_high

  , (n.ghi_wm2 + n.dni_wm2) / 2.0 AS solar_score

FROM stg_eccc_hourly e
JOIN stg_nasa_power_hourly n
  ON e.latitude = n.latitude
 AND e.longitude = n.longitude
 AND e.timestamp_utc = n.timestamp_utc ;