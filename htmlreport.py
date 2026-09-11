import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
db_host = os.getenv("db_host", "localhost")
db_user = os.getenv("db_user", "root")
db_password = os.getenv("db_password", "")
db_name = os.getenv("db_name", "weather_db")

# create sqlalchemy engine to eliminate pandas read_sql UserWarning
engine = create_engine(f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}/{db_name}")
con = engine.connect()

# read the single source of truth from disk (Address reviewer feedback: no duplicated SQL strings)
base_dir = os.path.dirname(os.path.abspath(__file__))
sql_path = os.path.join(base_dir, "queries.sql")

with open(sql_path, "r", encoding="utf-8") as f:
    sql_text = f.read()

# split statements by semicolon and filter out empty lines or "USE database" commands
statements = [s.strip() for s in sql_text.split(";") if s.strip()]
queries = [s for s in statements if not s.lower().startswith("use ")]

#let pd read SQL code for 4 queries
query1 = queries[0]
pd1 = pd.read_sql(text(query1), con)
pd1.to_csv(os.path.join(base_dir, "query1.csv"), index=False)
htmltable1 = pd1.to_html(classes="table", index=False)

query2 = queries[1]
pd2 = pd.read_sql(text(query2), con)
pd2.to_csv(os.path.join(base_dir, "query2.csv"), index=False)
htmltable2 = pd2.to_html(classes="table", index=False)

query3 = queries[2]
pd3 = pd.read_sql(text(query3), con)
# strip "0 days " from the column
if "peakrain" in pd3.columns:
    pd3["peakrain"] = pd3["peakrain"].astype(str).str.replace("0 days ", "")
pd3.to_csv(os.path.join(base_dir, "query3.csv"), index=False)
htmltable3 = pd3.to_html(classes="table", index=False)

query4 = queries[3]
pd4 = pd.read_sql(text(query4), con)
pd4.to_csv(os.path.join(base_dir, "query4.csv"), index=False)
htmltable4 = pd4.to_html(classes="table", index=False)

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

output_path = os.path.join(base_dir, "htmlqueriesreport.html")
with open(output_path, "w", encoding="utf-8") as qu:
    qu.write(website_page)

print("HTML report and all 4 CSV files generated.")