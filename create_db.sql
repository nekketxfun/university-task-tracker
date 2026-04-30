CREATE DATABASE uni_tracker_db;
CREATE USER tracker_admin WITH PASSWORD '1488228';
GRANT ALL PRIVILEGES ON DATABASE uni_tracker_db TO tracker_admin;
-- Если используете PG 15+:
\c uni_tracker_db
GRANT ALL ON SCHEMA public TO tracker_admin;