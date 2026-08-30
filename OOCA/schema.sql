create database if not exists weather_db;

use weather_db; -- if it exists then no create, prevents dupes

create table if not exists hr_weather(city varchar(50) not null, forecast_time datetime not null, temp float, rain_chance int, 
primary key(city, forecast_time));  -- primary keys make sure that dupes are checked from both columns instead of one

