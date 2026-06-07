# MindFlow — Authentication System

## Overview
Pure Python · PyMySQL · bcrypt · No framework

## Architecture

```
server.py               ← stdlib HTTPServer + router
│
├── routes/auth_routes.py       ← HTTP handlers (register, login, logout, me)
│
├── services/auth_service.py    ← Business logic layer
│   ├── AuthService.register()
│   ├── AuthService.login()
│   ├── AuthService.logout()
│   ├── AuthService.get_current_user()
│   └── AuthService.change_password()
│
├── models/
│   ├── user.py                 ← User dataclass + UserRepository (SQL)
│   └── session.py              ← Session dataclass + SessionRepository (SQL)
│
└── utils/
    ├── password.py             ← bcrypt hash / verify / strength check
    ├── token.py                ← Secure session token generation (HMAC)
    ├── validators.py           ← Email, name, field validation
    ├── middleware.py           ← require_auth / require_admin decorators
    └── response.py             ← ok / bad_request / unauthorized helpers
```

## API Endpoints

| Method | Path                        | Auth | Description            |
|--------|-----------------------------|------|------------------------|
| POST   | /api/auth/register          | ✗    | Create new account     |
| POST   | /api/auth/login             | ✗    | Login, get session     |
| POST   | /api/auth/logout            | ✓    | Invalidate session     |
| GET    | /api/auth/me                | ✓    | Get current user       |
| POST   | /api/auth/change-password   | ✓    | Change password        |
| POST   | /api/auth/logout-all        | ✓    | Kill all sessions      |

## Security Features
- bcrypt with 12 rounds (~250ms per hash)
- Constant-time password comparison (no timing attacks)
- Generic "invalid credentials" error (prevents user enumeration)
- HttpOnly + SameSite=Strict session cookie
- Session stored server-side in MySQL (stateful)
- Automatic session expiry (1 day / 30 days with remember_me)
- Password rehash on login if work factor changes
- Forced logout of all devices on password change

## Running
```bash
pip install -r requirements.txt
cp .env.example .env   # fill in DB credentials
mysql -u root -p < database/schema.sql
mysql -u root -p mindflow_db < database/migrations/v004_add_sessions.sql
python server.py
```

## Testing
```bash
python -m unittest tests/test_auth.py -v
```
