@echo off
echo ====================================
echo MARIS Research Intelligence System
echo ====================================
echo.

REM Check if .env file exists
if not exist .env (
    echo ❌ .env file not found!
    echo Please create .env file with: GOOGLE_API_KEY=your_key_here
    pause
    exit /b 1
)

echo ✅ .env file found
echo 🚀 Starting MARIS server...
echo.
echo 🌐 Server will be available at: http://localhost:8000
echo 📖 API docs at: http://localhost:8000/docs
echo.
echo 💡 Press Ctrl+C to stop the server
echo.

REM Start with uvicorn directly
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level info

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Server failed to start
    echo.
    echo 🔧 Troubleshooting:
    echo 1. Make sure Python is installed
    echo 2. Install dependencies: pip install -r requirements.txt
    echo 3. Check GOOGLE_API_KEY in .env file
    echo 4. Try: python start_minimal.py
    pause
    exit /b 1
)

echo.
echo ✅ Server stopped
pause
