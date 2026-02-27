@echo off
echo 🚀 Starting MARIS Frontend...
echo.

REM Check if node_modules exists
if not exist "node_modules" (
    echo 📦 Installing dependencies...
    npm install
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Check if .env file exists
if not exist ".env" (
    echo 📝 Creating .env file...
    echo VITE_API_URL=http://localhost:8000/api > .env
    echo ✅ Created .env file with API URL
)

echo 🌐 Starting development server...
echo.
echo 📍 Frontend will be available at: http://localhost:5173
echo 📍 Backend should be running at: http://localhost:8000
echo.
echo 💡 Press Ctrl+C to stop the server
echo.

npm run dev

pause
