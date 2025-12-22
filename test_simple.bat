@echo off
chcp 65001 >nul
echo Test SMS'leri gonderiliyor...
echo.
cd /d "%~dp0"
.\venv\Scripts\python.exe quick_test.py
pause

