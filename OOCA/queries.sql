use weather_db;

-- query 1 avg, max, min temp
select "Q1: Metrics" as query_name, city, date(forecast_time) as forecast_date,
round(avg(temp), 1) as temp_avg,
max(temp) as temp_max,
min(temp) as temp_min

from hr_weather

-- combines all 24 hours of each day for each city
group by city, date(forecast_time)
order by city, forecast_date;

-- query 2 temp range
select "Q2: Widest" as query_name, city,
max(temp) as temp_max,
min(temp) as temp_min,
round(max(temp) - min(temp), 1) as temp_range

from hr_weather
group by city
order by temp_range desc

-- return only top record
limit 1;

-- query 3 rain chance
-- partition by resets counter to 1 on each new day
with rainrank as(select city,
date(forecast_time) as forecast_date,
time(forecast_time) as peakrain, rain_chance,
row_number() over(partition by city, date(forecast_time)
order by rain_chance desc, forecast_time asc) as rain_rank
from hr_weather)

select "Q3: Rain Chance" as query_name, city, forecast_date,
peakrain, rain_chance as max_rain_chance
from rainrank
where rain_rank = 1
order by city, forecast_date;

-- query 4 day temp change
-- hours into daily record
with dailyavg as(select city, date(forecast_time) as forecast_date, 
round(avg(temp), 1) as dailyavgtemp
from hr_weather
group by city, date(forecast_time))

-- lag to return one row previous
-- second lag to calc net temp change (tempdiff variable)
-- over to specify that it is a window function
select "Q4: Day Temp Change" as query_name, city, forecast_date,
dailyavgtemp, lag(dailyavgtemp, 1) over(partition by city order by
forecast_date) as prevdayavgtemp, round(dailyavgtemp - lag(dailyavgtemp, 1)
over(partition by city order by forecast_date), 1) 
as tempdiff

from dailyavg
order by city, forecast_date;