# Weather Summary Report README
## 7-Day Report from Weather API of 5 Thai Cities

### This is a readme file for my OOCA task (the analysis of weather report data of 5 different Thai cities):

### Schema Design
* Single Table Design (`hr_weather`): Only 840 rows are needed for a 7-day run, so a single table is the most appropriate. I kept it as simple as possible so that the system wouldn't take a lot of processing time.
* Composite Primary Key (`city, forecast_time`): I linked these two variables together in order to prevent duplicate-type errors. They uniquely identify each hourly record per location.

### Idempotency
* `on duplicate key update`: In my `def weather()` function, I use this line to prevent duplicates by updating just temperature and rain chance, not city and forecast time. This makes it so that re-running does not produce duplicate rows.
* Re-run Safety and Testing: I made it so that if the ingestion script were to run multiple times, it would just update the data with the latest metrics rather than creating duplicate entries or errors. To actually prove this, I checked the database count after my first run (840 rows) and immediately ran the script a second time. The row count stayed at exactly 840, and running `checkdata.sql` returned 0 duplicates, proving that consecutive runs are completely safe.

### Data Issues & Fixes
* Timestamp Formatting Mismatch: The Open-Meteo API returns timestamps with a `T` in between the date and time (like `2026-09-11T00:00`), which SQL cannot read properly as a `DATETIME`. I fixed this by replacing `T` with a space and adding `:00` for seconds.
* API Error Catching: At first, I wrote `resp.raise_for_status` without parentheses, so HTTP errors wouldn't trigger properly. I added `()` to make it run and expanded the `try-except` block to catch `KeyError` and `ValueError` alongside connection issues so bad data won't crash the script.
* Terminal Directory Pathing: Running scripts from different terminal folders caused `FileNotFoundError` when searching for `schema.sql`. I fixed this by using `os.path.abspath(__file__)` so the script always finds its files no matter where you execute the command.

### 24/7 Update Changes & Big Data
If I were to update this to be a script that updates every hour forever, then I would definitely:
* Change from a manual Python script to an orchestration tool like **Apache Airflow** to schedule runs, manage retries, and monitor pipeline errors automatically.
* Partition my SQL table by month using `PARTITION BY RANGE (TO_DAYS(forecast_time))`. Since 5 cities updating 168 hours of sliding forecasts every day would add around 300,000+ rows in a year, partitioning lets MySQL scan only the recent partition instead of checking the whole multi-year table. Dropping a month of old data is also instant with `DROP PARTITION`.
* Use connection pools and SQLAlchemy so that I don't have to open and close raw database connections repeatedly for every request.

### Interesting Things from the Data
* Temperature Range (Chiang Mai Widest Swing): In Query 2, **Chiang Mai** recorded the widest temperature fluctuation over the 7-day period with a range of **11.1°C** (reaching a maximum of 33.1°C and dropping to a minimum of 22.0°C)[cite: 4]. By comparison, coastal Phuket experienced the narrowest variation in the dataset with only a 7.3°C spread (from 23.7°C to 31.0°C)[cite: 4]. Northern inland valley areas experience sharper shifts between daytime direct solar radiation and nocturnal cooling compared to maritime-buffered southern coastal regions.
* Peak Rain Probability & Diurnal Patterns: Across most cities in Query 3, the highest rain chances consistently strike during the afternoon and early evening between **14:00:00 and 18:00:00** due to daytime convective cloud build-up[cite: 4]. Both **Phuket** and **Hat Yai** recorded days with a guaranteed **100%** peak rain chance[cite: 4]. However, night and early-morning precipitation events also occur, such as Bangkok recording its peak rain probability of 91% right at midnight (**00:00:00**) on 2026-09-11[cite: 4].
* Query 3 Deterministic Tie-Breaking: When multiple hours within the same day share the exact same maximum rain percentage, `ROW_NUMBER()` ordered by `rain_chance DESC, forecast_time ASC` guarantees that the earliest hour is selected deterministically without generating conflicting duplicate rows[cite: 4].
* Day-over-Day Temperature Drift (Query 4): Using `LAG()` reveals noticeable day-to-day weather shifts[cite: 4]. Chiang Mai experienced the sharpest single-day warming jump in the dataset on 2026-09-13, with its daily average rising by **+2.0°C** (from 25.4°C to 27.4°C), followed by a cooling trend dropping by -1.4°C and -1.1°C over consecutive days[cite: 4]. Meanwhile, Khon Kaen experienced the largest sudden cooling drop on 2026-09-13, falling by **-1.8°C** in a single day[cite: 4].

### Supply Chain & Logistics Relevance
These weather metrics directly match common data tasks in supply chain engineering:
* Running 5 cities hourly is like tracking daily order demand across 5 regional distribution centers.
* Query 1 (Daily Min/Avg/Max) is identical to calculating daily SKU sales volume to plan baseline warehouse stock[cite: 4].
* Query 2 (Temperature Range) acts like a demand volatility check; higher volatility means a facility needs a larger safety stock buffer[cite: 4].
* Query 3 (Peak Rain Hours) works just like identifying peak delivery truck arrival windows so warehouse managers know when to schedule loading dock workers[cite: 4].
* Query 4 (Day-to-Day Temp Change using `LAG`) tracks trend shifts from yesterday to today, which is the same as monitoring day-over-day shipment changes to spot supply disruptions early[cite: 4].

### AI Tools Usage
> I used AI tools to help me debug my code. When I write code, I visualize an overall flow first before writing, but I often spend too much time debugging or not knowing a specific function that would help me more than the ones I know. AI is handy because of this. When I learned coding in university, I would often get stuck on debugging—the logic was right and the functions seemed right, but errors would still pop up. With AI, I can share the terminal tracebacks and error messages to pinpoint what went wrong, which saves huge amounts of time and lets me focus on building the logic.

---

### How to Run This Project

### Installation & Environment Setup

#### 1. Clone the Repository
Open your terminal or command prompt and clone the project directory:
```bash
git clone [https://github.com/Seet0/Weather-Report-Analysis-OOCA-.git](https://github.com/Seet0/Weather-Report-Analysis-OOCA-.git)
cd Weather-Report-Analysis-OOCA-
```

#### 2. Create and Activate a Virtual Environment (Optional but Recommended)
Keep your project dependencies isolated from global packages:

* Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

* macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Required Packages
Install all libraries pinned in `requirements.txt`:
```bash
pip install -r requirements.txt
```

#### 4. Configure Database Credentials
Create a `.env` file in the root directory by copying `.env.example`:
```bash
cp .env.example .env
```

Open `.env` and fill in your local MySQL connection details:
```ini
db_host=localhost
db_user=root
db_password=your_mysql_password
db_name=weather_db
```

#### 5. Verify MySQL Server Status
Ensure your local MySQL service is running on port 3306. The database `weather_db` and table `hr_weather` will be initialized automatically from `schema.sql` on the initial run.

---

### Execution Steps

1. **Run Ingestion Pipeline:**
   ```bash
   python OOCAtest.py
   ```
   *Initializes `hr_weather`, pulls all 5 cities from Open-Meteo, saves raw JSON files in `/rawdata`, and loads 840 rows.*

2. **Generate HTML & CSV Reports:**
   ```bash
   python htmlreport.py
   ```
   *Reads queries from `queries.sql`, creates `query1.csv` through `query4.csv`, and writes `htmlqueriesreport.html`.*

3. **Check Data (MySQL Workbench):**
   * Open and run `checkdata.sql` to verify that there are 840 rows, 168 rows per city, and 0 duplicate records.