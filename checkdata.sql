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