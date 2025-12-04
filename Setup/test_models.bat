@echo off
REM Test Model Integration Script

echo ==================================
echo Testing Model Integration
echo ==================================
echo.

REM Check if Docker is running
docker-compose ps | findstr "dpe-backend" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Backend container not running
    echo Start with: docker-compose up -d
    exit /b 1
)

echo Backend container is running
echo.

REM Check model files
echo Checking model files in container...
docker-compose exec backend ls -lh /app/models/

echo.
echo Running model verification...
docker-compose exec backend python verify_models.py

echo.
echo ==================================
echo Test Complete!
echo ==================================
pause
