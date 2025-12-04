# Quick Setup Guide (No Docker Required!)

## Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

## Installation

### 1. Create Virtual Environment
```powershell
cd d:\projects\PredixX
python -m venv venv
.\venv\Scripts\activate
```

### 2. Install Dependencies
```powershell
cd dpe-backend
pip install -r requirements.txt
```

### 3. Initialize Database
```powershell
# Run Alembic migrations to create tables
alembic upgrade head
```

### 4. Start the Backend
```powershell
python start.py
```

The API will be available at:
- **API:** http://localhost:8000
- **Docs:** http://localhost:8000/docs
- **Health:** http://localhost:8000/health

## Features
✅ SQLite database (no PostgreSQL needed)  
✅ Background tasks (no Redis/Celery needed)  
✅ ML model integration  
✅ JWT authentication  
✅ Auto-reload on code changes  

## Quick Test
```powershell
# Register a user
curl -X POST http://localhost:8000/api/v1/auth/register `
  -H "Content-Type: application/json" `
  -d '{\"email\": \"test@example.com\", \"password\": \"test123\", \"role\": \"merchant\"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login `
  -H "Content-Type: application/json" `
  -d '{\"email\": \"test@example.com\", \"password\": \"test123\"}'
```

## Development
- Edit files in `app/` - server auto-reloads
- View logs in terminal
- Database file: `dpe.db` (SQLite)

## Production Notes
For production, consider:
- Using PostgreSQL instead of SQLite
- Setting up proper task queue (Celery + Redis)
- Using process manager (PM2, systemd, supervisor)
- Adding HTTPS/SSL
- Configuring proper SECRET_KEY in .env file
