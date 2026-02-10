-- Migration: 01_init_telemetry.sql
-- Description: Creates the brooder_telemetry table for time-series data.
-- Optimized for: Supabase (PostgreSQL) and low-latency dashboards.

-- 1. Create the Telemetry Table
-- Using TIMESTAMPTZ is crucial for handling multiple timezones in distributed farms.
create table if not exists brooder_telemetry (
  id bigint generated always as identity primary key,
  device_id text not null,
  timestamp timestamptz not null default now(),
  temperature float,
  humidity float,
  ammonia_ppm float,
  
  -- Store raw JSON payload for debugging or schema evolution transparency
  raw_data jsonb,
  
  -- Metadata for auditing
  created_at timestamptz default now()
);

-- 2. Create Optimized Indexes
-- Use a composite index for typical "Dashboard Queries":
-- "Show me the last 24h of data for Device X"
create index if not exists idx_telemetry_device_time 
on brooder_telemetry (device_id, timestamp desc);

-- 3. Enable Row Level Security (RLS) - Best Practice
alter table brooder_telemetry enable row level security;

-- Policy: Allow Insert from authenticated service role (our script) and Select for public (dashboard)
-- Note: You might want to restrict Select in production.
create policy "Enable insert for service key" 
on brooder_telemetry for insert 
with check (true);

create policy "Enable read access for all" 
on brooder_telemetry for select 
using (true);
