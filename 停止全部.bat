@echo off
chcp 65001 >nul
echo ========================================
echo   正在停止所有 OpenManus 服务...
echo ========================================
echo.
taskkill /FI "WINDOWTITLE eq OpenManus-Backend" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq OpenManus-Frontend" /F >nul 2>&1
echo 所有服务已停止。
echo.
pause
