@echo off
REM Dynamic Pricing Engine - Quick Start Script for Windows

echo Starting Dynamic Pricing Engine Setup...
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Docker is not installed. Please install Docker first.
    exit /b 1
)

docker-compose --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

REM Create environment files if they don't exist
if not exist "dpe-backend\.env" (
    echo Creating backend .env file...
    copy "dpe-backend\.env.example" "dpe-backend\.env"
)

if not exist "dpe-frontend\.env.local" (
    echo Creating frontend .env.local file...
    copy "dpe-frontend\.env.local.example" "dpe-frontend\.env.local"
)

REM Start services
echo Starting Docker containers...
docker-compose up -d

REM Wait for services to be healthy
echo Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Run migrations
echo Running database migrations...
docker-compose exec -T backend alembic upgrade head

echo.
echo Setup complete!
echo.
echo Services are running at:
echo    - Frontend:  http://localhost:3000
echo    - Backend:   http://localhost:8000
echo    - API Docs:  http://localhost:8000/api/v1/docs
echo.
echo Next steps:
echo    1. Open http://localhost:3000 in your browser
echo    2. Register a new account
echo    3. Start creating products and optimizing prices!
echo.
echo To view logs:
echo    docker-compose logs -f
echo.
echo To stop services:
echo    docker-compose down
echo.
pause
