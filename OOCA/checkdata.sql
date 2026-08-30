use weather_db;

--  check total row count (should be 840)
select COUNT(*) as total_rows from hr_weather;

-- make sure that all 5 cities have 168 rows
select city, COUNT(*) as hourly_records
from hr_weather
group by city;