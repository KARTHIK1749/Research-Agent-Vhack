@echo off
echo 🚀 Starting MARIS Servers
echo =====================
echo.

echo 📍 Starting Backend on Port 8000...
start "MARIS Backend" cmd /k "cd /d backend && python start_with_debug.py"

echo 📍 Waiting for backend to start...
timeout /t 3 /nobreak >nul

echo 📍 Starting Frontend on Port 8173...
start "MARIS Frontend" cmd /k "cd /d frontend && npm run dev"

echo.
echo ✅ Servers starting...
echo 🌐 Frontend: http://localhost:8173
echo 🔧 Backend:  http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo 💡 Close this window. Servers will continue running in separate windows.
pause
