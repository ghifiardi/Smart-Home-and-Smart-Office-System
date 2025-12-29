-- Initialize TimescaleDB extension and setup hypertables

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Enable pgvector extension for face recognition embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Note: Actual tables will be created by Alembic migrations
-- This script just sets up the extensions

-- After tables are created by Alembic, run:
-- SELECT create_hypertable('device_states', 'timestamp');
-- SELECT create_hypertable('detections', 'timestamp');
-- SELECT create_hypertable('events', 'timestamp');

-- Create retention policies (30 days for raw data)
-- SELECT add_retention_policy('device_states', INTERVAL '90 days');
-- SELECT add_retention_policy('detections', INTERVAL '90 days');
-- SELECT add_retention_policy('events', INTERVAL '365 days');

-- Create continuous aggregates for analytics
-- CREATE MATERIALIZED VIEW detections_hourly
-- WITH (timescaledb.continuous) AS
-- SELECT
--   time_bucket('1 hour', timestamp) AS hour,
--   zone_id,
--   object_class,
--   COUNT(*) as count,
--   AVG(confidence) as avg_confidence
-- FROM detections
-- GROUP BY hour, zone_id, object_class;

-- Add policy to refresh the view
-- SELECT add_continuous_aggregate_policy('detections_hourly',
--   start_offset => INTERVAL '3 hours',
--   end_offset => INTERVAL '1 hour',
--   schedule_interval => INTERVAL '1 hour');
