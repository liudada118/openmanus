@echo off
chcp 65001 >nul
echo ========================================
echo   Stopping OpenManus services...
echo ========================================
echo.

echo [1/3] Stopping backend window...
taskkill /FI "WINDOWTITLE eq OpenManus-Backend" /F >nul 2>&1

echo [2/3] Stopping frontend window...
taskkill /FI "WINDOWTITLE eq OpenManus-Frontend" /F >nul 2>&1

echo [3/3] Cleaning up ports 8002 and 3000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8002" ^| findstr "LISTENING"') do (
    taskkill /f /pid %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000" ^| findstr "LISTENING"') do (
    taskkill /f /pid %%a >nul 2>&1
)

echo.
echo ========================================
echo   All services stopped.
echo ========================================
pause
