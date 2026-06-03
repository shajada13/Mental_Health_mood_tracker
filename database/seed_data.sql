-- ============================================================
--  MindFlow — Seed / Demo Data
-- ============================================================
USE mindflow_db;

-- Demo users (passwords = 'Password123!' bcrypt hashed)
INSERT INTO users (full_name, email, password_hash, date_of_birth, gender, primary_goal, stress_baseline, onboarding_complete, is_active, is_verified)
VALUES
('Sarah Williams',  'sarah@demo.com',  '$2b$12$demo_hash_sarah',  '1996-05-10', 'female',          'reduce_stress',  7, TRUE, TRUE, TRUE),
('James Carter',    'james@demo.com',  '$2b$12$demo_hash_james',  '1990-03-22', 'male',             'improve_sleep',  5, TRUE, TRUE, TRUE),
('Priya Sharma',    'priya@demo.com',  '$2b$12$demo_hash_priya',  '1998-11-15', 'female',           'improve_mood',   6, TRUE, TRUE, TRUE);

-- User preferences
INSERT INTO user_preferences (user_id, daily_checkin_reminder, reminder_time, weekly_report_enabled, emergency_alerts_enabled, timezone)
VALUES
(2, TRUE, '20:00:00', TRUE, TRUE, 'America/New_York'),
(3, TRUE, '21:00:00', TRUE, TRUE, 'Asia/Kolkata'),
(4, TRUE, '19:30:00', TRUE, TRUE, 'America/Los_Angeles');

-- Mood entries (last 7 days for Sarah)
INSERT INTO moods (user_id, mood_score, mood_label, stress_level, sleep_hours, energy_level, activities, note, check_in_date)
VALUES
(2, 3, 'okay',  6, 6.5, 5, '["work"]',                          'Bit stressed about deadline',        DATE_SUB(CURDATE(), INTERVAL 6 DAY)),
(2, 2, 'bad',   8, 5.0, 3, '["work"]',                          'Overwhelmed with tasks',             DATE_SUB(CURDATE(), INTERVAL 5 DAY)),
(2, 3, 'okay',  7, 6.0, 4, '["exercise","work"]',               'Evening walk helped',                DATE_SUB(CURDATE(), INTERVAL 4 DAY)),
(2, 4, 'good',  5, 7.5, 6, '["exercise","meditation"]',         'Meditation session was great',       DATE_SUB(CURDATE(), INTERVAL 3 DAY)),
(2, 4, 'good',  4, 8.0, 7, '["reading","socializing"]',         'Nice dinner with friends',           DATE_SUB(CURDATE(), INTERVAL 2 DAY)),
(2, 5, 'great', 3, 8.5, 8, '["exercise","meditation","reading"]','Best day this week!',               DATE_SUB(CURDATE(), INTERVAL 1 DAY)),
(2, 4, 'good',  4, 7.5, 7, '["exercise"]',                      'Feeling focused today',              CURDATE());

-- Journal entries
INSERT INTO journals (user_id, title, content, mood_snapshot, tags, sentiment_score, sentiment_label, is_private)
VALUES
(2, 'Rough Week',
 'Feeling a bit overwhelmed today due to work pressure, but the evening walk helped me relax and clear my head.',
 3, '["work","stress","exercise"]', -0.15, 'neutral', TRUE),
(2, 'Getting Better',
 'I have been trying to meditate every morning and I notice my anxiety has decreased significantly. Small wins!',
 4, '["meditation","anxiety","progress"]', 0.65, 'positive', TRUE),
(2, 'Gratitude Entry',
 'Grateful for my friends, my health, and the small moments of joy I find every day. Life is good.',
 5, '["gratitude","happiness","friends"]', 0.90, 'very_positive', TRUE);

-- Emergency contacts
INSERT INTO emergency_contacts (user_id, full_name, relationship, contact_type, phone, email, preferred_contact, alert_on_high_stress, alert_on_crisis)
VALUES
(2, 'Mary Williams',   'parent',    'primary',      '+1987654321', 'mary@example.com',   'both', TRUE,  TRUE),
(2, 'Emma Johnson',    'friend',    'secondary',    '+1876543210', 'emma@example.com',   'sms',  TRUE,  TRUE),
(2, 'Dr. John Smith',  'therapist', 'professional', '+1654321098', 'drsmith@clinic.com', 'email',FALSE, TRUE);

-- AI Report
INSERT INTO ai_reports (user_id, report_type, period_start, period_end, avg_mood_score, avg_stress_level, avg_sleep_hours, total_checkins, mood_trend, summary, key_patterns, recommendations, risk_assessment)
VALUES (
    2, 'weekly',
    DATE_SUB(CURDATE(), INTERVAL 7 DAY),
    CURDATE(),
    3.57, 5.29, 7.14, 7,
    'improving',
    'Sarah showed consistent improvement this week. Mood rose from 2 (Bad) to 5 (Great) over 7 days. Exercise and meditation correlated strongly with higher mood scores.',
    '[{"pattern":"Stress peaks on weekdays","confidence":0.87},{"pattern":"Exercise improves next-day mood by 1.2 points","confidence":0.92},{"pattern":"Sleep under 6hrs correlates with bad mood","confidence":0.85}]',
    '[{"type":"exercise","title":"Morning Walk","reason":"You feel better on days you exercise"},{"type":"meditation","title":"5-Min Breathing","reason":"Reduces your stress level by avg 2 points"},{"type":"sleep","title":"Sleep by 10pm","reason":"You score higher mood with 8+ hrs sleep"}]',
    'none'
);

-- Notifications
INSERT INTO notifications (user_id, type, channel, title, body, risk_level, status, sent_at)
VALUES
(2, 'daily_reminder', 'in_app', 'Time for your daily check-in!',
 'How are you feeling today? Take 2 minutes to log your mood.', 'none', 'read', NOW()),
(2, 'ai_insight', 'in_app', 'AI Insight: Exercise is your superpower',
 'You feel 1.2 points better on days you exercise. Try to keep it up!', 'none', 'delivered', NOW()),
(2, 'weekly_report', 'email', 'Your Weekly Wellness Report is ready',
 'Great news — your mood improved this week! Tap to view full report.', 'none', 'sent', NOW());

