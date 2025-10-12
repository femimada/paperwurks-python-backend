-- Initialize PostgreSQL database for Paperwurks
-- This script runs automatically on first container startup

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create additional databases if needed
-- CREATE DATABASE paperwurks_test;

-- Set up recommended PostgreSQL settings for Django
ALTER SYSTEM SET timezone = 'Europe/London';
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_duration = 'on';

-- Grant privileges
-- GRANT ALL PRIVILEGES ON DATABASE paperwurks_dev TO postgres;