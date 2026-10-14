CREATE DATABASE IF NOT EXISTS explore_india
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE explore_india;

CREATE TABLE IF NOT EXISTS destinations (
  id INT PRIMARY KEY,
  zone VARCHAR(80),
  state VARCHAR(120),
  city VARCHAR(120),
  name VARCHAR(255) NOT NULL,
  attraction_type VARCHAR(120),
  establishment_year VARCHAR(50),
  visit_hours DECIMAL(6,2),
  rating DECIMAL(3,2),
  entrance_fee DECIMAL(10,2),
  airport_nearby VARCHAR(20),
  weekly_off VARCHAR(100),
  significance VARCHAR(100),
  dslr_allowed VARCHAR(20),
  review_lakhs DECIMAL(12,3),
  best_time VARCHAR(100),
  INDEX idx_destination_state (state),
  INDEX idx_destination_type (attraction_type),
  INDEX idx_destination_rating (rating)
);

CREATE TABLE IF NOT EXISTS favorites (
  visitor_id VARCHAR(80) NOT NULL,
  destination_id INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(visitor_id, destination_id),
  CONSTRAINT fk_favorite_destination FOREIGN KEY(destination_id)
    REFERENCES destinations(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS trip_plans (
  id INT AUTO_INCREMENT PRIMARY KEY,
  visitor_id VARCHAR(80) NOT NULL,
  title VARCHAR(255),
  budget DECIMAL(10,2),
  hours_available DECIMAL(8,2),
  total_fee DECIMAL(10,2),
  total_hours DECIMAL(8,2),
  items_json LONGTEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS quiz_results (
  id INT AUTO_INCREMENT PRIMARY KEY,
  visitor_id VARCHAR(80) NOT NULL,
  score INT NOT NULL,
  total INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Example analytics query: number of attractions and average rating per state.
SELECT state, COUNT(*) AS attraction_count, ROUND(AVG(rating), 2) AS average_rating
FROM destinations
GROUP BY state
ORDER BY attraction_count DESC;

-- Example analytics query: popular attractions by review count.
SELECT name, city, state, rating, review_lakhs
FROM destinations
ORDER BY review_lakhs DESC
LIMIT 10;
