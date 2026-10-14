"""Import the cleaned tourism CSV into MySQL. Configure .env first."""
from dotenv import load_dotenv
load_dotenv()
import os
import pandas as pd
import mysql.connector

if not os.getenv("MYSQL_HOST"):
    raise SystemExit("Set MYSQL_HOST in .env before running this MySQL importer.")

conn = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"), port=int(os.getenv("MYSQL_PORT", "3306")),
    user=os.getenv("MYSQL_USER", "root"), password=os.getenv("MYSQL_PASSWORD", ""),
    database=os.getenv("MYSQL_DATABASE", "explore_india")
)
df = pd.read_csv("data/cleaned_tourist_data.csv")
columns = [
    "Zone", "State", "City", "Name", "Type", "Establishment Year",
    "time needed to visit in hrs", "Google review rating", "Entrance Fee in INR",
    "Airport with 50km Radius", "Weekly Off", "Significance", "DSLR Allowed",
    "Number of google review in lakhs", "Best Time to visit"
]
sql = """INSERT INTO destinations
(id, zone, state, city, name, attraction_type, establishment_year, visit_hours,
 rating, entrance_fee, airport_nearby, weekly_off, significance, dslr_allowed,
 review_lakhs, best_time)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
ON DUPLICATE KEY UPDATE name=VALUES(name), rating=VALUES(rating), entrance_fee=VALUES(entrance_fee)"""
cur = conn.cursor()
for index, row in df.iterrows():
    vals = [index + 1]
    for col in columns:
        value = row.get(col)
        if pd.isna(value) or str(value).strip().lower() in ("not specified", "nan", ""):
            value = None
        vals.append(value)
    cur.execute(sql, vals)
conn.commit()
cur.close()
conn.close()
print(f"Imported {len(df)} destinations into MySQL.")
