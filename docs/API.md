# MindFlow API Reference

Base URL: `http://localhost:5000/api`

## Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/register | Register new user |
| POST | /auth/login | Login user |
| POST | /auth/logout | Logout user |
| GET  | /auth/me | Get current user |

## Mood
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /mood/checkin | Submit mood check-in |
| GET  | /mood/history | Get mood history |
| GET  | /mood/stats | Get mood statistics |

## Journal
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | /journal | Get all entries |
| POST | /journal | Create entry |
| PUT  | /journal/:id | Update entry |
| DELETE | /journal/:id | Delete entry |

## Emergency
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | /emergency/contacts | Get contacts |
| POST | /emergency/contacts | Add contact |
| POST | /emergency/alert | Trigger alert |
| GET  | /emergency/logs | Alert history |

## AI
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /ai/chat | Chat with AI |
| GET  | /ai/insights | Get AI insights |
| GET  | /ai/recommendations | Get recommendations |
