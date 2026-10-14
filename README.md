# Explore India — Tourism Analytics & Smart Trip Planner

A full-stack DVP mini-project built with HTML, CSS, JavaScript, Python Flask, and SQL. It uses the tourism CSV supplied with the original assignment (325 attractions, 15 columns).

## Features
- Responsive travel-themed frontend
- Search and filter destinations by query, state, category, rating and fee
- Destination details and saved favorites
- Budget- and time-aware trip planner
- Tourism analytics with interactive Plotly charts
- Destination quiz with scoring
- CSV export for destinations and itinerary
- MySQL support, with SQLite demo mode so the project can be previewed without setting up MySQL first

## Quick start in VS Code (Windows)

1. Extract the project ZIP.
2. Open the `explore_india_project` folder in VS Code.
3. Open Terminal → New Terminal.
4. Create and activate a virtual environment:

   ```powershell
   py -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use Command Prompt:

   ```bat
   venv\Scripts\activate.bat
   ```

5. Install packages:

   ```powershell
   pip install -r requirements.txt
   ```

6. Copy `.env.example` to `.env`. For the easiest first run, leave `MYSQL_HOST` blank. The app uses a local SQLite database and imports the cleaned CSV automatically on first start.
7. Run the app:

   ```powershell
   python app.py
   ```

8. Open `http://127.0.0.1:5000` in your browser.

## Enable MySQL

1. Install and start MySQL Server.
2. Open MySQL Workbench or the MySQL command-line client.
3. Run `schema.sql`.
4. Copy `.env.example` to `.env` and set `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, and `MYSQL_DATABASE`.
5. Install requirements with `pip install -r requirements.txt`.
6. Import the CSV:

   ```powershell
   python seed_data.py
   ```

7. Start the website:

   ```powershell
   python app.py
   ```

The application selects MySQL when `MYSQL_HOST` is configured; otherwise it uses SQLite demo mode. Never put database credentials in JavaScript or HTML.

## Project structure

- `app.py` — Flask routes and API
- `database.py` — SQLite/MySQL connectivity and table initialization
- `services.py` — SQL queries, analytics, recommendations, trip planning, favorites
- `exports.py` — CSV and PDF helper functions
- `schema.sql` — MySQL schema and sample analytics queries
- `seed_data.py` — CSV-to-MySQL importer
- `templates/` — HTML pages
- `static/css/style.css` — responsive styling
- `static/js/` — interactive frontend
- `data/` — source datasets and local SQLite demo database

## Important data notes
- The current dataset contains destination names, locations, types, visitor ratings, fees, duration, facilities, review counts, and best visiting time.
- Images shown in cards are illustrative image mappings from Unsplash and are not verified official images for every attraction. An image fallback appears if an image fails to load.
- The trip planner estimates entrance fees and visiting durations only. It does not calculate transport, accommodation, or food.
- Favorites and saved plans use a browser-session visitor identifier rather than a full login system.
- This project is an academic demo and not a live booking service.

## Main API endpoints
- `GET /api/dashboard`
- `GET /api/destinations`
- `GET /api/destinations/<id>`
- `GET /api/filters`
- `GET /api/recommendations`
- `POST /api/plan`
- `GET /api/favorites`
- `POST /api/favorites/<id>`
- `GET /api/analytics`
- `GET /api/quiz/questions`
- `POST /api/quiz/submit`
- `GET /api/export/destinations.csv`

## SQL examples

```sql
-- Most highly rated destinations
SELECT name, state, city, rating
FROM destinations
ORDER BY rating DESC
LIMIT 10;

-- Average rating by state
SELECT state, ROUND(AVG(rating), 2) AS average_rating, COUNT(*) AS attractions
FROM destinations
GROUP BY state
ORDER BY attractions DESC;

-- Most affordable attractions with ratings above 4.0
SELECT name, state, entrance_fee, rating
FROM destinations
WHERE rating >= 4.0
ORDER BY entrance_fee ASC
LIMIT 20;
```
