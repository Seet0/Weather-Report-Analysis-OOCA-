# Weather Summary Report README
## 7-Day Report from Weather API of 5 Thai Cities

### This is a readme file for my OOCA task (the analysis of weather report data of 5 different Thai cities):

### Schema Design
* Single Table Design (`hr_weather`): Only 840 rows are needed, so single tables are most appropriate. I kept it as simple as possible
so that the system wouldn't take a lot of processing time.
* Composite Primary Key (`city, forecast_time`): I linked these two variables together in order to prevent duplicate-type errors. 
They also uniquely identify each hourly record per location.

### Idempotency
* `on duplicate key update`: In my `def weather()` function, I use this line to prevent duplicates by updating just temperature and rain chance,
not city and forecast time. This makes it so that there will not be 840 duplicate rows.
* Re-run Safety: I made it so that if the ingestion script were to run multiple times, it would just update the data with the latest metrics rather than creating duplicate entries or errors. `primary key(city, forecast_time)` This line in `schema.sql` ensures me that the 
database will never allow two rows with the exact same city and forecast time.

### Data Issues
* Timestamp Formatting Mismatch: The most annoying thing I came across was the weather API website (Open-Meteo) returning dissimilar timestamp
fromatting with respect to SQL. I spent quite some time figuring out why there were errors and had to search up why my timestamps weren't working
as intended. 

### 24/7 Update Changes
If I were to update this to be a script that updates every hour forever, then I would definitely:
* change from a manual Python script to something bigger such as **Apache Airflow** to author, schedule, and monitor complex data workflows and pipelines.
* partition my SQL data by month/year in order to prevent lag (such as deleting old data points, MySQL scanning every row in the table for queries).
* use connection pools so that I don't have to open and close a new connection for every single request.

### Interesting Things from the Data
* Phuket maintained steady temperatures compared to Chiang Mai, which meant that cities near the coast experiences little to no changes while cities to the north
have higher temperature fluctuations.
* The peak rain chances in August seem to be during the afternoon. This is most likely because we are in the rainy season right now. 

### AI Tools Usage
> I used AI tools to help me debug my code. When I write code, I visualize an overall flow first before writing, but I often spend too much time debugging
or not knowing a specific function that would help me more than the ones I know (one comparison would be if I were to use repeated statements instead of a for loop).
AI is handy because of this. When I learned coding in university, I would often get stuck on debugging. The logic was right, the functions seem right, but errors just pop up whenever and wherever. I oftentimes get frustrated and have to take breaks to clear my head. With the AI era, I can just screenshot the errors and AI will tell me what exactly I got wrong, saving time by almost 90% and increasing my work efficiency by around 50%.