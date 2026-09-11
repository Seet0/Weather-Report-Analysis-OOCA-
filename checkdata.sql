use weather_db;

--  check total row count (should be 840)
-- won't change on an immediate run again on the same day
select COUNT(*) as total_rows from hr_weather;

-- make sure that all 5 cities have 168 rows
select city, COUNT(*) as hourly_records
from hr_weather
group by city;

-- check for dupes (returns 0 rows if none)
select city, forecast_time, COUNT(*) AS duplicate_count
from hr_weather
group by city, forecast_time
having COUNT(*) > 1;

-- sanity check to detect impossible values or out-of-bounds readings
select 
    city,
    COUNT(*) as total_rows,
    SUM(case when temp < 0 or temp > 50 then 1 else 0 end) as anomalous_temps,
    SUM(case when rain_chance < 0 or rain_chance > 100 then 1 else 0 end) as invalid_rain_probs
from hr_weather
group by city;