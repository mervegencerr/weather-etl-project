
# 1.

SELECT
  DATE(timestamp_utc) AS day
  , AVG(solar_score) AS avg_solar_score
FROM final_weather_report
GROUP BY day
ORDER BY avg_solar_score DESC
LIMIT 1 ;

------------------------------------------------------------------------------------------------

# 2.

SELECT
  DATE(timestamp_utc) AS day
  , SUM(ghi_wm2) AS total_ghi
FROM final_weather_report
GROUP BY day
ORDER BY total_ghi DESC
LIMIT 1 ;

-----------------------------------------------------------------------------------------------

# 3.

SELECT 
  STRFTIME('%H', timestamp_utc) AS hour_of_day
  , SUM(wind_flag_high) AS events
FROM final_weather_report
GROUP BY hour_of_day
ORDER BY events DESC
LIMIT 1 ;

----------------------------------------------------------------------------------------------

# 4. 

WITH values AS (

  SELECT
    COUNT(*)                                    AS total
    , SUM(air_temp_c)                             AS sum_temp
    , SUM(ghi_wm2)                                AS sum_ghi
    , SUM(air_temp_c * air_temp_c)                AS sum_temp_square
    , SUM(ghi_wm2 * ghi_wm2)                      AS sum_ghi_square
    , SUM(air_temp_c * ghi_wm2)                   AS sum_temp_times_ghi
  FROM final_weather_report
  WHERE air_temp_c IS NOT NULL AND ghi_wm2 IS NOT NULL

)

SELECT
  (1.0 * (n * sum_temp_times_ghi - sum_temp * sum_ghi)) /
  NULLIF(
    SQRT(
      (n * sum_temp_square - sum_temp * sum_temp) * (n * sum_ghi_square - sum_ghi * sum_ghi)
    ),
    0
  ) AS correlation
FROM values ;

---------------------------------------------------------------------------------------------

# 5.

SELECT DISTINCT
  STRFTIME('%H', timestamp_utc) AS hour_of_day
  , temp_anomaly_c
  , ghi_wm2
FROM final_weather_report
ORDER BY ABS(temp_anomaly_c) DESC
LIMIT 5 ;

----------------------------------------------------------------------------------------------