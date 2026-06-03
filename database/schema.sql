-- ============================================================
--  MindFlow — Mental Health Mood Tracker
--  Complete MySQL Database Schema
--  Version: 1.0
--  Engine: InnoDB | Charset: utf8mb4
-- ============================================================

DROP DATABASE IF EXISTS mindflow_db;
CREATE DATABASE mindflow_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE mindflow_db;

-- ============================================================
-- 1. USERS
-- ============================================================
CREATE TABLE users (
    id                    INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    full_name             VARCHAR(100)  NOT NULL,
    email                 VARCHAR(150)  NOT NULL UNIQUE,
    password_hash         VARCHAR(255)  NOT NULL,
    date_of_birth         DATE,
    gender                ENUM('male','female','non_binary','prefer_not_to_say') DEFAULT 'prefer_not_to_say',
    avatar_url            VARCHAR(500),
    primary_goal          ENUM('reduce_stress','improve_sleep','improve_mood','self_growth','other') DEFAULT 'improve_mood',
    stress_baseline       TINYINT UNSIGNED DEFAULT 5 COMMENT 'Baseline stress 1-10 set at onboarding',
    onboarding_complete   BOOLEAN NOT NULL DEFAULT FALSE,
    is_active             BOOLEAN NOT NULL DEFAULT TRUE,
    is_verified           BOOLEAN NOT NULL DEFAULT FALSE,
    last_login_at         TIMESTAMP NULL,
    created_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT chk_stress_baseline CHECK (stress_baseline BETWEEN 1 AND 10)
);

-- ============================================================
-- 2. ADMIN
-- ============================================================
CREATE TABLE admin (
    id                    INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id               INT UNSIGNED NOT NULL UNIQUE COMMENT 'Admin linked to a user account',
    role                  ENUM('super_admin','moderator','support') NOT NULL DEFAULT 'support',
    permissions           JSON COMMENT 'e.g. {"manage_users":true,"view_reports":true}',
    last_action_at        TIMESTAMP NULL,
    created_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_admin_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- ============================================================
-- 3. MOODS
-- ============================================================
CREATE TABLE moods (
    id                    INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id               INT UNSIGNED NOT NULL,
    mood_score            TINYINT UNSIGNED NOT NULL COMMENT '1=Awful 2=Bad 3=Okay 4=Good 5=Great',
    mood_label            ENUM('awful','bad','okay','good','great') NOT NULL,
    stress_level          TINYINT UNSIGNED NOT NULL DEFAULT 5 COMMENT '1-10 scale',
    sleep_hours           DECIMAL(4,1) COMMENT 'Hours slept last night',
    energy_level          TINYINT UNSIGNED COMMENT '1-10 scale',
    activities            JSON COMMENT '["exercise","meditation","reading","socializing","other"]',
    note                  TEXT COMMENT 'Optional short check-in note',
    location              VARCHAR(100) COMMENT 'Optional location context',
    weather               VARCHAR(50)  COMMENT 'Optional weather context',
    check_in_date         DATE NOT NULL COMMENT 'The date this check-in refers to',
    created_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_mood_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT chk_mood_score
        CHECK (mood_score BETWEEN 1 AND 5),

    CONSTRAINT chk_stress_level
        CHECK (stress_level BETWEEN 1 AND 10),

    CONSTRAINT chk_energy_level
        CHECK (energy_level BETWEEN 1 AND 10 OR energy_level IS NULL),

    CONSTRAINT chk_sleep_hours
        CHECK (sleep_hours BETWEEN 0 AND 24 OR sleep_hours IS NULL),

    -- One check-in per user per day
    CONSTRAINT uq_mood_user_date
        UNIQUE (user_id, check_in_date)
);

-- Indexes for fast mood history queries
CREATE INDEX idx_mood_user_date ON moods (user_id, check_in_date DESC);
CREATE INDEX idx_mood_score     ON moods (mood_score);

-- ============================================================
-- 4. JOURNALS
-- ============================================================
CREATE TABLE journals (
    id                    INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id               INT UNSIGNED NOT NULL,
    mood_id               INT UNSIGNED NULL COMMENT 'Optional link to a mood check-in',
    title                 VARCHAR(200),
    content               LONGTEXT NOT NULL,
    mood_snapshot         TINYINT UNSIGNED COMMENT 'Mood score at time of writing (1-5)',
    tags                  JSON COMMENT '["anxiety","work","family","gratitude"]',
    sentiment_score       DECIMAL(4,3) COMMENT 'AI sentiment -1.000 to 1.000',
    sentiment_label       ENUM('very_negative','negative','neutral','positive','very_positive'),
    word_count            SMALLINT UNSIGNED GENERATED ALWAYS AS (
                              CHAR_LENGTH(content) - CHAR_LENGTH(REPLACE(content,' ','')) + 1
                          ) STORED,
    is_private            BOOLEAN NOT NULL DEFAULT TRUE,
    is_flagged            BOOLEAN NOT NULL DEFAULT FALSE COMMENT 'Flagged by AI for crisis content',
    created_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_journal_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT fk_journal_mood
        FOREIGN KEY (mood_id) REFERENCES moods(id)
        ON DELETE SET NULL ON UPDATE CASCADE,

    CONSTRAINT chk_sentiment
        CHECK (sentiment_score BETWEEN -1.000 AND 1.000 OR sentiment_score IS NULL)
);

CREATE INDEX idx_journal_user_date ON journals (user_id, created_at DESC);
CREATE INDEX idx_journal_flagged   ON journals (is_flagged);
CREATE FULLTEXT INDEX idx_journal_content ON journals (title, content);

-- ============================================================
-- 5. AI REPORTS
-- ============================================================
CREATE TABLE ai_reports (
    id                    INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id               INT UNSIGNED NOT NULL,
    report_type           ENUM('weekly','monthly','insight','recommendation','crisis') NOT NULL,
    period_start          DATE NOT NULL,
    period_end            DATE NOT NULL,

    -- Aggregated stats
    avg_mood_score        DECIMAL(3,2) COMMENT 'Average mood over the period',
    avg_stress_level      DECIMAL(3,2),
    avg_sleep_hours       DECIMAL(4,2),
    total_checkins        SMALLINT UNSIGNED DEFAULT 0,
    total_journal_entries SMALLINT UNSIGNED DEFAULT 0,
    mood_trend            ENUM('improving','declining','stable','fluctuating') DEFAULT 'stable',

    -- AI-generated content
    summary               TEXT NOT NULL COMMENT 'AI-generated narrative summary',
    key_patterns          JSON COMMENT '[{"pattern":"stress peaks on weekdays","confidence":0.87}]',
    recommendations       JSON COMMENT '[{"type":"exercise","title":"Morning Walk","reason":"..."}]',
    risk_assessment       ENUM('none','low','moderate','high','critical') DEFAULT 'none',
    risk_factors          JSON COMMENT '["social_isolation","sleep_deprivation"]',

    -- Metadata
    ai_model_version      VARCHAR(30) DEFAULT 'gpt-4o',
    generated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_read               BOOLEAN NOT NULL DEFAULT FALSE,
    created_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_ai_report_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT chk_period
        CHECK (period_end >= period_start)
);

CREATE INDEX idx_ai_report_user_type ON ai_reports (user_id, report_type, generated_at DESC);
CREATE INDEX idx_ai_report_risk      ON ai_reports (risk_assessment);

-- ============================================================
-- 6. EMERGENCY CONTACTS
-- ============================================================
CREATE TABLE emergency_contacts (
    id                    INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id               INT UNSIGNED NOT NULL,
    full_name             VARCHAR(100) NOT NULL,
    relationship          ENUM('parent','sibling','partner','friend','colleague','therapist','doctor','other') NOT NULL,
    contact_type          ENUM('primary','secondary','professional') NOT NULL DEFAULT 'secondary',
    phone                 VARCHAR(20)  NOT NULL,
    email                 VARCHAR(150),
    preferred_contact     ENUM('sms','email','both') NOT NULL DEFAULT 'sms',
    alert_on_high_stress  BOOLEAN NOT NULL DEFAULT TRUE,
    alert_on_crisis       BOOLEAN NOT NULL DEFAULT TRUE,
    alert_on_daily_summary BOOLEAN NOT NULL DEFAULT FALSE,
    is_active             BOOLEAN NOT NULL DEFAULT TRUE,
    last_alerted_at       TIMESTAMP NULL,
    created_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_contact_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    -- Max 5 emergency contacts per user
    CONSTRAINT uq_contact_user_phone UNIQUE (user_id, phone)
);

CREATE INDEX idx_contact_user   ON emergency_contacts (user_id, contact_type);
CREATE INDEX idx_contact_active ON emergency_contacts (is_active);

-- ============================================================
-- 7. NOTIFICATIONS
-- ============================================================
CREATE TABLE notifications (
    id                    INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id               INT UNSIGNED NOT NULL,
    contact_id            INT UNSIGNED NULL COMMENT 'If alert was sent to an emergency contact',
    ai_report_id          INT UNSIGNED NULL COMMENT 'If triggered by an AI report',
    mood_id               INT UNSIGNED NULL COMMENT 'If triggered by a mood check-in',

    type                  ENUM(
                              'daily_reminder',
                              'weekly_report',
                              'monthly_report',
                              'ai_insight',
                              'emergency_alert',
                              'crisis_alert',
                              'contact_alerted',
                              'system',
                              'welcome',
                              'streak'
                          ) NOT NULL,

    channel               ENUM('in_app','email','sms','push') NOT NULL DEFAULT 'in_app',
    title                 VARCHAR(200) NOT NULL,
    body                  TEXT NOT NULL,
    data                  JSON COMMENT 'Extra payload e.g. {"risk_level":"high","mood_score":2}',

    status                ENUM('pending','sent','delivered','failed','read') NOT NULL DEFAULT 'pending',
    error_message         VARCHAR(500) COMMENT 'If status=failed, reason here',
    risk_level            ENUM('none','low','moderate','high','critical') DEFAULT 'none',

    scheduled_at          TIMESTAMP NULL COMMENT 'For scheduled notifications',
    sent_at               TIMESTAMP NULL,
    read_at               TIMESTAMP NULL,
    created_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_notif_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT fk_notif_contact
        FOREIGN KEY (contact_id) REFERENCES emergency_contacts(id)
        ON DELETE SET NULL ON UPDATE CASCADE,

    CONSTRAINT fk_notif_ai_report
        FOREIGN KEY (ai_report_id) REFERENCES ai_reports(id)
        ON DELETE SET NULL ON UPDATE CASCADE,

    CONSTRAINT fk_notif_mood
        FOREIGN KEY (mood_id) REFERENCES moods(id)
        ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE INDEX idx_notif_user_status ON notifications (user_id, status, created_at DESC);
CREATE INDEX idx_notif_type        ON notifications (type);
CREATE INDEX idx_notif_risk        ON notifications (risk_level);
CREATE INDEX idx_notif_scheduled   ON notifications (scheduled_at, status);

-- ============================================================
-- 8. USER PREFERENCES (extends users)
-- ============================================================
CREATE TABLE user_preferences (
    id                        INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id                   INT UNSIGNED NOT NULL UNIQUE,
    daily_checkin_reminder    BOOLEAN NOT NULL DEFAULT TRUE,
    reminder_time             TIME NOT NULL DEFAULT '20:00:00',
    weekly_report_enabled     BOOLEAN NOT NULL DEFAULT TRUE,
    monthly_report_enabled    BOOLEAN NOT NULL DEFAULT TRUE,
    ai_insights_enabled       BOOLEAN NOT NULL DEFAULT TRUE,
    emergency_alerts_enabled  BOOLEAN NOT NULL DEFAULT TRUE,
    theme                     ENUM('light','dark','system') NOT NULL DEFAULT 'light',
    language                  VARCHAR(10) NOT NULL DEFAULT 'en',
    timezone                  VARCHAR(50) NOT NULL DEFAULT 'UTC',
    data_sharing_consent      BOOLEAN NOT NULL DEFAULT FALSE,
    created_at                TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at                TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_pref_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- ============================================================
-- 9. MOOD STREAKS (gamification)
-- ============================================================
CREATE TABLE mood_streaks (
    id                    INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id               INT UNSIGNED NOT NULL UNIQUE,
    current_streak        SMALLINT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'Consecutive check-in days',
    longest_streak        SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    last_checkin_date     DATE,
    total_checkins        INT UNSIGNED NOT NULL DEFAULT 0,
    created_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_streak_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- ============================================================
-- 10. COMMUNITY POSTS (optional social)
-- ============================================================
CREATE TABLE community_posts (
    id                    INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id               INT UNSIGNED NOT NULL,
    content               TEXT NOT NULL,
    is_anonymous          BOOLEAN NOT NULL DEFAULT FALSE,
    is_visible            BOOLEAN NOT NULL DEFAULT TRUE,
    is_flagged            BOOLEAN NOT NULL DEFAULT FALSE,
    likes_count           INT UNSIGNED NOT NULL DEFAULT 0,
    comments_count        INT UNSIGNED NOT NULL DEFAULT 0,
    created_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_post_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- ============================================================
-- 11. AUDIT LOG (admin / security)
-- ============================================================
CREATE TABLE audit_logs (
    id                    BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id               INT UNSIGNED NULL COMMENT 'NULL for system actions',
    admin_id              INT UNSIGNED NULL,
    action                VARCHAR(100) NOT NULL COMMENT 'e.g. user.login, mood.create, alert.sent',
    entity_type           VARCHAR(50)  COMMENT 'e.g. users, moods, journals',
    entity_id             INT UNSIGNED COMMENT 'ID of the affected record',
    old_values            JSON COMMENT 'Snapshot before change',
    new_values            JSON COMMENT 'Snapshot after change',
    ip_address            VARCHAR(45)  COMMENT 'IPv4 or IPv6',
    user_agent            VARCHAR(500),
    created_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_audit_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE SET NULL ON UPDATE CASCADE,

    CONSTRAINT fk_audit_admin
        FOREIGN KEY (admin_id) REFERENCES admin(id)
        ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE INDEX idx_audit_user   ON audit_logs (user_id, created_at DESC);
CREATE INDEX idx_audit_action ON audit_logs (action);

-- ============================================================
-- VIEWS
-- ============================================================

-- User dashboard summary view
CREATE VIEW v_user_dashboard AS
SELECT
    u.id                             AS user_id,
    u.full_name,
    u.email,
    ms.current_streak,
    ms.longest_streak,
    ms.total_checkins,
    ROUND(AVG(m.mood_score), 2)      AS avg_mood_7d,
    ROUND(AVG(m.stress_level), 2)    AS avg_stress_7d,
    ROUND(AVG(m.sleep_hours), 2)     AS avg_sleep_7d,
    COUNT(j.id)                      AS journal_entries_total,
    MAX(m.check_in_date)             AS last_checkin_date
FROM users u
LEFT JOIN mood_streaks ms ON ms.user_id = u.id
LEFT JOIN moods m  ON m.user_id = u.id
    AND m.check_in_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
LEFT JOIN journals j ON j.user_id = u.id
GROUP BY u.id, u.full_name, u.email, ms.current_streak, ms.longest_streak, ms.total_checkins;

-- Active emergency contacts view
CREATE VIEW v_active_emergency_contacts AS
SELECT
    ec.*,
    u.full_name AS user_name,
    u.email     AS user_email
FROM emergency_contacts ec
JOIN users u ON u.id = ec.user_id
WHERE ec.is_active = TRUE;

-- Unread high-risk notifications view
CREATE VIEW v_high_risk_notifications AS
SELECT
    n.*,
    u.full_name,
    u.email
FROM notifications n
JOIN users u ON u.id = n.user_id
WHERE n.risk_level IN ('high','critical')
  AND n.status != 'read'
ORDER BY n.created_at DESC;

-- ============================================================
-- TRIGGERS
-- ============================================================

DELIMITER $$

-- Auto-create user_preferences row on new user
CREATE TRIGGER trg_user_preferences_insert
AFTER INSERT ON users
FOR EACH ROW
BEGIN
    INSERT INTO user_preferences (user_id) VALUES (NEW.id);
    INSERT INTO mood_streaks (user_id) VALUES (NEW.id);
END$$

-- Update streak on mood check-in
CREATE TRIGGER trg_update_streak
AFTER INSERT ON moods
FOR EACH ROW
BEGIN
    DECLARE last_date DATE;
    DECLARE cur_streak SMALLINT UNSIGNED;

    SELECT last_checkin_date, current_streak
    INTO last_date, cur_streak
    FROM mood_streaks
    WHERE user_id = NEW.user_id;

    IF last_date = DATE_SUB(NEW.check_in_date, INTERVAL 1 DAY) THEN
        -- Consecutive day: increment streak
        UPDATE mood_streaks
        SET current_streak    = cur_streak + 1,
            longest_streak    = GREATEST(longest_streak, cur_streak + 1),
            last_checkin_date = NEW.check_in_date,
            total_checkins    = total_checkins + 1
        WHERE user_id = NEW.user_id;
    ELSEIF last_date < DATE_SUB(NEW.check_in_date, INTERVAL 1 DAY) OR last_date IS NULL THEN
        -- Streak broken or first check-in
        UPDATE mood_streaks
        SET current_streak    = 1,
            last_checkin_date = NEW.check_in_date,
            total_checkins    = total_checkins + 1
        WHERE user_id = NEW.user_id;
    END IF;
END$$

-- Auto-flag journal if contains crisis keywords
CREATE TRIGGER trg_flag_crisis_journal
BEFORE INSERT ON journals
FOR EACH ROW
BEGIN
    IF NEW.content REGEXP '(suicid|self.harm|end my life|kill myself|want to die|no reason to live)' THEN
        SET NEW.is_flagged = TRUE;
    END IF;
END$$

-- Audit log on user delete
CREATE TRIGGER trg_audit_user_delete
BEFORE DELETE ON users
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (user_id, action, entity_type, entity_id, old_values)
    VALUES (OLD.id, 'user.delete', 'users', OLD.id,
            JSON_OBJECT('email', OLD.email, 'full_name', OLD.full_name));
END$$

DELIMITER ;

-- ============================================================
-- STORED PROCEDURES
-- ============================================================

DELIMITER $$

-- Get full user dashboard data
CREATE PROCEDURE sp_get_dashboard(IN p_user_id INT UNSIGNED)
BEGIN
    SELECT * FROM v_user_dashboard WHERE user_id = p_user_id;

    SELECT * FROM moods
    WHERE user_id = p_user_id
    ORDER BY check_in_date DESC
    LIMIT 7;

    SELECT * FROM journals
    WHERE user_id = p_user_id
    ORDER BY created_at DESC
    LIMIT 3;

    SELECT * FROM ai_reports
    WHERE user_id = p_user_id
      AND is_read = FALSE
    ORDER BY generated_at DESC
    LIMIT 1;
END$$

-- Send emergency alert (log notification + update contact)
CREATE PROCEDURE sp_trigger_emergency_alert(
    IN p_user_id      INT UNSIGNED,
    IN p_risk_level   VARCHAR(20),
    IN p_trigger_note TEXT
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    -- Create in-app crisis notification for user
    INSERT INTO notifications (user_id, type, channel, title, body, risk_level, status)
    VALUES (
        p_user_id,
        'crisis_alert',
        'in_app',
        'High Stress Detected',
        p_trigger_note,
        p_risk_level,
        'sent'
    );

    -- Queue SMS/email alerts to all active emergency contacts
    INSERT INTO notifications (user_id, contact_id, type, channel, title, body, risk_level, status)
    SELECT
        p_user_id,
        ec.id,
        'emergency_alert',
        CASE ec.preferred_contact WHEN 'email' THEN 'email' ELSE 'sms' END,
        CONCAT('Alert: ', (SELECT full_name FROM users WHERE id = p_user_id), ' may need your support'),
        p_trigger_note,
        p_risk_level,
        'pending'
    FROM emergency_contacts ec
    WHERE ec.user_id   = p_user_id
      AND ec.is_active = TRUE
      AND ec.alert_on_crisis = TRUE;

    COMMIT;
END$$

DELIMITER ;

-- ============================================================
-- SEED: Default admin user
-- ============================================================
INSERT INTO users (full_name, email, password_hash, is_active, is_verified, onboarding_complete)
VALUES ('MindFlow Admin', 'admin@mindflow.app',
        '$2b$12$placeholder_bcrypt_hash_here', TRUE, TRUE, TRUE);

INSERT INTO admin (user_id, role, permissions)
VALUES (1, 'super_admin',
        '{"manage_users":true,"view_reports":true,"manage_alerts":true,"manage_admin":true}');

