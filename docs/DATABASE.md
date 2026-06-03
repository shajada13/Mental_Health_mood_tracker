# MindFlow Database Documentation

## Tables Overview

| Table | Purpose | Key Relationships |
|-------|---------|-------------------|
| `users` | Core user accounts | Parent to all tables |
| `admin` | Admin roles & permissions | 1:1 with users |
| `moods` | Daily mood check-ins | Belongs to users |
| `journals` | Journal entries | Belongs to users, optional mood link |
| `ai_reports` | AI-generated insights | Belongs to users |
| `emergency_contacts` | Trusted contacts | Belongs to users |
| `notifications` | All alerts & messages | Links users, contacts, reports, moods |
| `user_preferences` | User settings | 1:1 with users (auto-created via trigger) |
| `mood_streaks` | Gamification streaks | 1:1 with users (auto-created via trigger) |
| `community_posts` | Optional social feed | Belongs to users |
| `audit_logs` | Security audit trail | Links users & admin |

## Key Constraints
- One mood check-in per user per day (`UNIQUE user_id + check_in_date`)
- Max 1 admin record per user (`UNIQUE user_id` on admin table)
- Sentiment score validated between -1.000 and 1.000
- Mood score validated between 1-5
- Stress/energy level validated between 1-10

## Triggers
- `trg_user_preferences_insert` — Auto-creates preferences + streak row on new user
- `trg_update_streak` — Updates check-in streak on each mood entry
- `trg_flag_crisis_journal` — Auto-flags journals with crisis keywords
- `trg_audit_user_delete` — Logs user deletions to audit_logs

## Views
- `v_user_dashboard` — Aggregated 7-day stats per user
- `v_active_emergency_contacts` — Active contacts with user info
- `v_high_risk_notifications` — Unread high/critical risk alerts

## Stored Procedures
- `sp_get_dashboard(user_id)` — Returns all dashboard data in one call
- `sp_trigger_emergency_alert(user_id, risk_level, note)` — Logs and queues emergency alerts
