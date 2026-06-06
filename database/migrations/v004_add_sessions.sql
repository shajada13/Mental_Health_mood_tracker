-- ============================================================
--  MindFlow — Migration v004
--  Add sessions table for pure-Python session management
-- ============================================================
USE mindflow_db;

CREATE TABLE IF NOT EXISTS sessions (
    id           INT UNSIGNED    AUTO_INCREMENT PRIMARY KEY,
    user_id      INT UNSIGNED    NOT NULL,
    token        VARCHAR(512)    NOT NULL UNIQUE,
    ip_address   VARCHAR(45),
    user_agent   VARCHAR(500),
    is_active    BOOLEAN         NOT NULL DEFAULT TRUE,
    expires_at   TIMESTAMP       NOT NULL,
    created_at   TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_session_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- Fast token lookup
CREATE INDEX idx_session_token      ON sessions (token);
CREATE INDEX idx_session_user       ON sessions (user_id, is_active);
CREATE INDEX idx_session_expires    ON sessions (expires_at);

-- Add is_admin column to users (needed by admin middleware)
ALTER TABLE users
    ADD COLUMN IF NOT EXISTS is_admin BOOLEAN NOT NULL DEFAULT FALSE;
