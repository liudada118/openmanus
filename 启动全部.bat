@echo off
chcp 65001 >nul
echo ========================================
echo   OpenManus AI Agent
echo ========================================
echo.

REM === 自动检测安装目录 ===
set "BASE_DIR=%~dp0"
if exist "%BASE_DIR%OpenManus-GUI\api_server.py" (
    set "BACKEND_DIR=%BASE_DIR%OpenManus-GUI"
) else if exist "E:\openmanus\OpenManus-GUI\api_server.py" (
    set "BACKEND_DIR=E:\openmanus\OpenManus-GUI"
) else if exist "E:\OpenManus\OpenManus-GUI\api_server.py" (
    set "BACKEND_DIR=E:\OpenManus\OpenManus-GUI"
) else (
    echo [ERROR] OpenManus-GUI not found!
    echo Please check the installation path.
    pause
    exit /b 1
)

if exist "%BASE_DIR%web-ui\package.json" (
    set "FRONTEND_DIR=%BASE_DIR%web-ui"
) else if exist "E:\openmanus\web-ui\package.json" (
    set "FRONTEND_DIR=E:\openmanus\web-ui"
) else if exist "E:\OpenManus\web-ui\package.json" (
    set "FRONTEND_DIR=E:\OpenManus\web-ui"
) else (
    echo [ERROR] web-ui not found!
    echo Please check the installation path.
    pause
    exit /b 1
)

echo [INFO] Backend: %BACKEND_DIR%
echo [INFO] Frontend: %FRONTEND_DIR%
echo.

echo [1/2] Starting backend API server...
start "OpenManus-Backend" cmd /k "cd /d %BACKEND_DIR% && python api_server.py"

echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo [2/2] Starting frontend...
start "OpenManus-Frontend" cmd /k "cd /d %FRONTEND_DIR% && pnpm dev"

echo Waiting for frontend to start...
timeout /t 8 /nobreak >nul

echo.
echo ========================================
echo   Started! Opening browser...
echo ========================================
start http://localhost:3000

echo.
echo Tips:
echo   - Close this window will not affect running services
echo   - To stop: close "OpenManus-Backend" and "OpenManus-Frontend" windows
echo   - Or double-click "stop_all.bat"
pause
