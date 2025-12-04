# 🚀 Quick Setup Guide - Dynamic Pricing Engine

## Prerequisites Checklist

- [ ] Docker Desktop installed and running
- [ ] Git installed
- [ ] 8GB RAM minimum (16GB recommended)
- [ ] 10GB free disk space

## Setup Steps (5 minutes)

### Option 1: Quick Start with Scripts (Recommended)

**Windows:**
```powershell
cd d:\projects\PredixX
.\start.bat
```

**Linux/Mac:**
```bash
cd /path/to/PredixX
chmod +x start.sh
./start.sh
```

### Option 2: Manual Setup

1. **Clone and Navigate**
   ```bash
   cd d:\projects\PredixX
   ```

2. **Setup Environment Files**
   ```bash
   # Backend
   cd dpe-backend
   copy .env.example .env  # Windows
   # cp .env.example .env  # Linux/Mac
   
   # Frontend
   cd ..\dpe-frontend
   copy .env.local.example .env.local  # Windows
   # cp .env.local.example .env.local  # Linux/Mac
   cd ..
   ```

3. **Start Services**
   ```bash
   docker-compose up -d
   ```

4. **Wait for Services** (30 seconds)
   ```bash
   docker-compose ps
   ```
   All services should show "Up" status.

5. **Run Database Migrations**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

## Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/v1/docs
- **Redoc**: http://localhost:8000/api/v1/redoc

## First Login

1. Go to http://localhost:3000
2. Click "Sign up"
3. Create account:
   - Email: `admin@example.com`
   - Password: `admin123`
   - Role: `Admin`
4. Login with credentials
5. You'll be redirected to the dashboard

## Testing the API

### Via Swagger UI (Browser)
Go to http://localhost:8000/api/v1/docs

### Via cURL

**Register:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","role":"merchant"}'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

**Create Product** (replace TOKEN):
```bash
curl -X POST http://localhost:8000/api/v1/products \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "store_id": 1,
    "sku": "PROD-001",
    "title": "Test Product",
    "cost_price": 10.0,
    "current_price": 20.0,
    "min_price": 12.0,
    "max_price": 30.0,
    "inventory": 100,
    "stock_age_days": 0
  }'
```

## Troubleshooting

### Port Already in Use
If ports 3000, 8000, 5432, or 6379 are in use:

**Option 1**: Stop conflicting services
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

**Option 2**: Change ports in `docker-compose.yml`

### Database Connection Issues
```bash
# Check if postgres is running
docker-compose ps postgres

# View postgres logs
docker-compose logs postgres

# Restart postgres
docker-compose restart postgres
```

### Backend Not Starting
```bash
# View backend logs
docker-compose logs backend

# Common fix: Rebuild
docker-compose build backend
docker-compose up -d backend
```

### Frontend Build Errors
```bash
# Install dependencies manually
cd dpe-frontend
docker-compose exec frontend npm install
docker-compose restart frontend
```

## Common Commands

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart a service
docker-compose restart backend

# Stop all services
docker-compose down

# Stop and remove volumes (CAUTION: Deletes data)
docker-compose down -v

# Rebuild services
docker-compose build

# Enter a container shell
docker-compose exec backend bash
docker-compose exec frontend sh
```

## Development Mode

### Backend (Python)
```bash
cd dpe-backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend (Node.js)
```bash
cd dpe-frontend
npm install
npm run dev
```

### Worker (Celery)
```bash
cd dpe-backend
celery -A app.workers.celery_app worker --loglevel=info
```

## Next Steps

1. ✅ Register your first user
2. ✅ Create a store (via API or database)
3. ✅ Add products
4. ✅ Get price recommendations
5. ✅ Enable auto-pricing
6. ✅ Run simulations

## Need Help?

- Check `DPE_README.md` for full documentation
- View API docs: http://localhost:8000/api/v1/docs
- Check logs: `docker-compose logs -f`
- Open an issue on GitHub

---

**Setup Complete! 🎉**

Your Dynamic Pricing Engine is ready to optimize prices!
