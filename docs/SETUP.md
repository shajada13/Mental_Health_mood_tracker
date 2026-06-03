# MindFlow — Setup Guide

## Prerequisites
- Python 3.10+
- MySQL 8.0+
- Node.js (optional, for live reload)

## Installation

### 1. Clone & setup environment
```bash
git clone <repo>
cd mindflow
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment
```bash
cp .env.example .env
# Edit .env with your DB credentials and API keys
```

### 3. Setup database
```bash
mysql -u root -p < database/schema.sql
mysql -u root -p mindflow_db < database/seed_data.sql
```

### 4. Run the app
```bash
python app.py
# Visit http://localhost:5000
```
