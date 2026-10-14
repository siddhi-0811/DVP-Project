import os
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
ROOT = Path(__file__).resolve().parent
SQLITE_PATH = ROOT / "data" / "explore_india_demo.db"
DB_KIND = "mysql" if os.getenv("MYSQL_HOST") else "sqlite-demo"

def get_db():
    if DB_KIND == "mysql":
        import mysql.connector
        return mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", "3306")),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", ""),
            database=os.getenv("MYSQL_DATABASE", "explore_india"),
            autocommit=False
        )
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    ROOT.joinpath("data").mkdir(exist_ok=True)
    if DB_KIND == "mysql":
        import mysql.connector
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS destinations (
                id INT PRIMARY KEY,
                zone VARCHAR(80), state VARCHAR(120), city VARCHAR(120),
                name VARCHAR(255) NOT NULL, attraction_type VARCHAR(120),
                establishment_year VARCHAR(50), visit_hours DECIMAL(6,2),
                rating DECIMAL(3,2), entrance_fee DECIMAL(10,2),
                airport_nearby VARCHAR(20), weekly_off VARCHAR(100),
                significance VARCHAR(100), dslr_allowed VARCHAR(20),
                review_lakhs DECIMAL(12,3), best_time VARCHAR(100)
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                visitor_id VARCHAR(80) NOT NULL,
                destination_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY(visitor_id, destination_id),
                FOREIGN KEY(destination_id) REFERENCES destinations(id) ON DELETE CASCADE
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS trip_plans (
                id INT AUTO_INCREMENT PRIMARY KEY,
                visitor_id VARCHAR(80) NOT NULL,
                title VARCHAR(255), budget DECIMAL(10,2),
                hours_available DECIMAL(8,2), total_fee DECIMAL(10,2),
                total_hours DECIMAL(8,2), items_json LONGTEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS quiz_results (
                id INT AUTO_INCREMENT PRIMARY KEY,
                visitor_id VARCHAR(80) NOT NULL,
                score INT NOT NULL, total INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
        _seed_mysql()
    else:
        conn = get_db()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS destinations (
                id INTEGER PRIMARY KEY, zone TEXT, state TEXT, city TEXT,
                name TEXT NOT NULL, attraction_type TEXT, establishment_year TEXT,
                visit_hours REAL, rating REAL, entrance_fee REAL,
                airport_nearby TEXT, weekly_off TEXT, significance TEXT,
                dslr_allowed TEXT, review_lakhs REAL, best_time TEXT
            );
            CREATE TABLE IF NOT EXISTS favorites (
                visitor_id TEXT NOT NULL, destination_id INTEGER NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY(visitor_id, destination_id),
                FOREIGN KEY(destination_id) REFERENCES destinations(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS trip_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT, visitor_id TEXT NOT NULL,
                title TEXT, budget REAL, hours_available REAL, total_fee REAL,
                total_hours REAL, items_json TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT, visitor_id TEXT NOT NULL,
                score INTEGER NOT NULL, total INTEGER NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
        """)
        count = conn.execute("SELECT COUNT(*) FROM destinations").fetchone()[0]
        if count == 0:
            _seed_sqlite(conn)
        conn.commit()
        conn.close()

def _clean_value(v):
    if v is None:
        return None
    if isinstance(v, str):
        v = v.strip()
        if not v or v.lower() in {"nan", "none", "null", "not specified"}:
            return None
    return v

def _seed_sqlite(conn):
    import pandas as pd
    csv_path = ROOT / "data" / "cleaned_tourist_data.csv"
    df = pd.read_csv(csv_path)
    columns = [
        "Zone", "State", "City", "Name", "Type", "Establishment Year",
        "time needed to visit in hrs", "Google review rating", "Entrance Fee in INR",
        "Airport with 50km Radius", "Weekly Off", "Significance", "DSLR Allowed",
        "Number of google review in lakhs", "Best Time to visit"
    ]
    for idx, row in df.iterrows():
        values = [
            idx + 1, _clean_value(row.get(columns[0])), _clean_value(row.get(columns[1])),
            _clean_value(row.get(columns[2])), _clean_value(row.get(columns[3])),
            _clean_value(row.get(columns[4])), _clean_value(row.get(columns[5])),
            _clean_value(row.get(columns[6])), _clean_value(row.get(columns[7])),
            _clean_value(row.get(columns[8])), _clean_value(row.get(columns[9])),
            _clean_value(row.get(columns[10])), _clean_value(row.get(columns[11])),
            _clean_value(row.get(columns[12])), _clean_value(row.get(columns[13])),
            _clean_value(row.get(columns[14]))
        ]
        conn.execute("""
            INSERT INTO destinations
            (id, zone, state, city, name, attraction_type, establishment_year, visit_hours,
             rating, entrance_fee, airport_nearby, weekly_off, significance, dslr_allowed,
             review_lakhs, best_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, values)

def _seed_mysql():
    import pandas as pd
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM destinations")
    count = cur.fetchone()[0]
    if count == 0:
        df = pd.read_csv(ROOT / "data" / "cleaned_tourist_data.csv")
        cols = [
            "Zone", "State", "City", "Name", "Type", "Establishment Year",
            "time needed to visit in hrs", "Google review rating", "Entrance Fee in INR",
            "Airport with 50km Radius", "Weekly Off", "Significance", "DSLR Allowed",
            "Number of google review in lakhs", "Best Time to visit"
        ]
        sql = """INSERT INTO destinations
            (id, zone, state, city, name, attraction_type, establishment_year, visit_hours,
             rating, entrance_fee, airport_nearby, weekly_off, significance, dslr_allowed,
             review_lakhs, best_time)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        for idx, row in df.iterrows():
            vals = [idx + 1] + [_clean_value(row.get(c)) for c in cols]
            cur.execute(sql, vals)
        conn.commit()
    cur.close()
    conn.close()
