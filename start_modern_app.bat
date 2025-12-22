@echo off
echo ===========================================
echo SMS Modern App Baslatiliyor...
echo ===========================================

echo 1. Backend Baslatiliyor (Port 5000)...
start "SMS Backend" cmd /k "cd backend && ..\venv\Scripts\activate && python app.py"

echo 2. Frontend Baslatiliyor (Port 5173)...
start "SMS Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ===========================================
echo Basarili! 
echo Web arayuzu icin: http://localhost:5173
echo.
echo NOT: Android uygulamasini guncellemeyi unutmayin!
echo ===========================================
pause
