@echo off
title CalSnap - AI Calorie Tracker
echo ========================================
echo   CalSnap - AI Calorie Tracker
echo ========================================
echo.
echo Finding your local IP...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| find "IPv4"') do set IP=%%a
set IP=%IP: =%
echo.
echo Installing dependencies...
pip install fastapi uvicorn python-multipart httpx -q
echo.
echo ========================================
echo   LAPTOP:  http://127.0.0.1:8000
echo   PHONE:   http://%IP%:8000
echo ========================================
echo.
echo Press Ctrl+C to stop
echo.
python -m uvicorn main:app --host 0.0.0.0 --port 8000
pause
