import pandas as pd
import mysql.connector as sq
import os

# connect to SQL
con = sq.connect(host = "localhost", user = "root", password = "admin123", database = "weather_db")

#let pd read SQL code for 4 queries
query1 = """select "Q1: Metrics" as query_name, city, date(forecast_time) as forecast_date,
round(avg(temp), 1) as temp_avg,
max(temp) as temp_max,
min(temp) as temp_min
from hr_weather
group by city, date(forecast_time)
order by city, forecast_date;"""

pd1 = pd.read_sql(query1, con)
htmltable1 = pd1.to_html(classes = "table", index = False)

query2 = """select "Q2: Widest" as query_name, city,
max(temp) as temp_max,
min(temp) as temp_min,
round(max(temp) - min(temp), 1) as temp_range

from hr_weather
group by city
order by temp_range desc
limit 1;"""

pd2 = pd.read_sql(query2, con)
htmltable2 = pd2.to_html(classes = "table", index = False)

query3 = """with rainrank as(select city,
date(forecast_time) as forecast_date,
time(forecast_time) as peakrain, rain_chance,
row_number() over(partition by city, date(forecast_time)
order by rain_chance desc, forecast_time asc) as rain_rank
from hr_weather)

select "Q3: Rain Chance" as query_name, city, forecast_date,
peakrain, rain_chance as max_rain_chance
from rainrank
where rain_rank = 1
order by city, forecast_date;"""

pd3 = pd.read_sql(query3, con)
htmltable3 = pd3.to_html(classes = "table", index = False)

query4 = """with dailyavg as(select city, date(forecast_time) as forecast_date, 
round(avg(temp), 1) as dailyavgtemp
from hr_weather
group by city, date(forecast_time))

select "Q4: Day Temp Change" as query_name, city, forecast_date,
dailyavgtemp, lag(dailyavgtemp, 1) over(partition by city order by
forecast_date) as prevdayavgtemp, round(dailyavgtemp - lag(dailyavgtemp, 1)
over(partition by city order by forecast_date), 1) 
as tempdiff

from dailyavg
order by city, forecast_date"""

pd4 = pd.read_sql(query4, con)
htmltable4 = pd4.to_html(classes = "table", index = False)



# close it after all queries are set
con.close()

website_page = f"""
<!DOCTYPE html>
    <html>
        <head>
            <title>Weather Summary Report</title>
                <style>
                body {{font-family: "Times New Roman", Times, serif; margin: 40px; background-color: #CC4757;}} 
                .table {{border-collapse: collapse; width: 80%; max-width: 800px; margin-bottom: 25px; background: white; box-shadow: 0 2px 5px rgba(0,0,0,0.1);}}
                .table th, .table td {{padding: 6px 10px; text-align: center; border-bottom: 1px solid #DDD;}}
                .table th {{background-color: #B660CD; color: white;}}
                .table tr:hover {{background-color: #F1F1F1;}}

                h1, h2, p {{color: white;}}
                h1 {{font-size: 32px; text-decoration: underline;}}
                h2 {{margin-top: 40px; margin-bottom: 12px; font-size: 18px}}

                p {{font-size: 14px; font-style: italic;}}
                </style>
        </head>
        <body>
            <h1>Weather Summary Report of 5 Thai Cities</h1>
                <p>Data from MySQL Workbench database (<code>weather_db.hr_weather</code>)</p>

                    <h2>Query 1: Average, Max, and Min Temperatures per City per Day</h2>
                    {htmltable1}

                    <h2>Query 2: Widest Temperature Range over the Next 7 Days</h2>
                    {htmltable2}

                    <h2>Query 3: Highest Precipitation Probability per City per Day</h2>
                    {htmltable3}

                    <h2>Query 4: Temperature Difference between Previous and Current Day</h2>
                    {htmltable4}
        </body>
    </html>    
"""

with open("htmlqueriesreport.html", "w", encoding = "utf-8") as qu:
    qu.write(website_page)

print("HTML report generated.")