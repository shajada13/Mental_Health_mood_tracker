-- Migration v001: Initial schema
-- Run: mysql -u root -p mindflow_db < migrations/v001_init.sql
-- See schema.sql for full table definitions
ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_token VARCHAR(255) NULL;
