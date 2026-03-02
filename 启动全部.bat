@echo off
chcp 65001 >nul
echo ========================================
echo   OpenManus AI Agent 启动中...
echo ========================================
echo.

echo [1/2] 启动后端 API 服务...
start "OpenManus-Backend" cmd /k "cd /d E:\OpenManus\OpenManus-GUI && .\venv\Scripts\activate && python api_server.py"

echo 等待后端启动...
timeout /t 5 /nobreak >nul

echo [2/2] 启动前端界面...
start "OpenManus-Frontend" cmd /k "cd /d E:\OpenManus\web-ui && pnpm dev"

echo 等待前端启动...
timeout /t 8 /nobreak >nul

echo.
echo ========================================
echo   启动完成！正在打开浏览器...
echo ========================================
start http://localhost:5173

echo.
echo 提示：
echo   - 关闭此窗口不会影响已启动的服务
echo   - 要停止服务，请关闭 "OpenManus-Backend" 和 "OpenManus-Frontend" 两个黑色窗口
echo   - 或者双击 "停止全部.bat" 一键停止
pause
