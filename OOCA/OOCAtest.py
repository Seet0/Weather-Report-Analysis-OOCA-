import os
import requests as rq
import json
import time
import mysql.connector as sq

base_url = "https://api.open-meteo.com/v1/forecast" #attachable with other parameters of each city

#nested dicts to pull the parameters later (insert into url)
cities = {"Bangkok": {"lat": 13.7563, "long": 100.5018}, "Chiang Mai": {"lat": 18.7883, "long": 98.9853}, "Phuket": {"lat": 7.8804, "long": 98.3923}, "Khon Kaen":
          {"lat": 16.4322, "long": 102.8236}, "Hat Yai": {"lat": 7.0084, "long": 100.4767}}

rawdir = "rawdata"
os.makedirs(rawdir, exist_ok=True) #makes folder in current directory, exist_ok prevents crashes

# schema stuff for SQL
schema_file = "schema.sql"
db_config = {"host": "localhost","user": "root","pass": "admin123", "database": "weather_db"}

def db_ini():
    con = sq.connect(host = db_config["host"], user = db_config["user"], password = db_config["pass"], database = db_config["database"])
    curs = con.cursor() # cursor object acts as control mechanism used to execute SQL statements and retrieve results

    with open(schema_file, "r", encoding = "utf-8") as op:
        sql_comm = op.read()

    statements = sql_comm.split(";")
    for state in statements:
        clean_state = state.strip()
        if clean_state: 
            curs.execute(clean_state)

    con.commit() # permanently saves the database structure changes to the server
    curs.close() # close channels
    con.close()
    print("Database initialized from schema.sql")





# weather function
def weather():
    starttime = time.time() #exact time, can calculate elapsed time
    city_success = 0 # literally just add 1 every time it succeeds
    city_failed = [] # make as a list to see which failed
    total_rows = 0

    db_ini() # pull from database function
    con = sq.connect(host = db_config["host"], user = db_config["user"], password = db_config["pass"], database = db_config["database"])
    curs = con.cursor()
    query = """insert into hr_weather(city, forecast_time, temp, rain_chance) values (%s, %s, %s, %s) 
    on duplicate key update temp = values(temp), rain_chance = values(rain_chance)""" # prevent dupes by just updating temp and rain chance


    print("Ingestion starting") #need for logs


# EXTRACT
#https://api.open-meteo.com/v1/forecast?latitude=13.7563&longitude=100.5018&hourly=temperature_2m,precipitation_probability&timezone=Asia%2FBangkok
#this is for each city's URL so that we don't have to have 5 long lines of codes for the 5 different cities

    for city, xyz in cities.items():
        para = {"latitude": xyz["lat"], "longitude": xyz["long"], "hourly": ["temperature_2m", "precipitation_probability"], "forecast_days": 7, "timezone": "Asia/Bangkok"}

    #I use try except to prevent half-filled rows

        try: 
            resp = rq.get(base_url, params = para, timeout = 15) #sys waits 15 seconds for resp
            resp.raise_for_status #checks status if OK, if not then go except

            data = resp.json() #converts json text into python

            fp = os.path.join(rawdir, f"{city.lower().replace(' ', '_')}.json") #file name will be hat_yai.json, and joins paths to make it simple and quick

            # w is write mode and utf-8 is international character writing failsafe
            with open(fp, "w", encoding = "utf-8") as x:
                json.dump(data, x, indent=2)


            hr = data["hourly"]
            times = hr["time"]
            temps = hr["temperature_2m"]
            rains = hr["precipitation_probability"] # need to be same name as json files

            format_rows = []
            for i in range(len(times)):
                clean = times[i].replace("T", " ") + ":00" # changes the time format for SQL to read it (from YYYY-MM-DDTHH:MM to YYYY-MM-DD HH:MM:SS)
                format_rows.append((city, clean, temps[i], rains[i])) # makes it a complete database row

            curs.executemany(query, format_rows) # executes all at once, reducing lag
            con.commit() # stores in SQL database


            total_rows += len(format_rows)
            city_success += 1 
            print(f"SUCCESS: No errors for {city}") #f-string formats according to the city in the dictionary at that point

        except rq.exceptions.RequestException as err:
            city_failed.append(city, str(err))
            print(f"ERROR: For {city}, {err}")

    curs.close()
    con.close()

    sec = round(time.time() - starttime, 2) #end - start rounded to 2 decimal places

    #Log summary
    print("Log Summary")
    print(f"Number of cities attempted: {len(cities)}")
    print(f"Number of successes: {city_success}")
    print(f"Number of errors: {len(city_failed)}")
    print(f"Total time taken: {sec} seconds")

    if len(city_failed) > 0:
        print(f"Error Details: {city_failed}")

if __name__ == "__main__": # executes the functions in the IF function
    weather()




