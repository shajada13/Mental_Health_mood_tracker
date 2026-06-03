-- Migration v002: Add alert_logs table (superseded by notifications table in v1 schema)
-- Kept for reference — notifications table covers all alert logging
SELECT 'v002: alert system integrated into notifications table' AS migration_note;
