@echo off
chcp 65001 >nul 2>&1
title OpenManus UI 升级工具

echo.
echo ╔══════════════════════════════════════════════════╗
echo ║          OpenManus UI 界面升级工具               ║
echo ║   将默认界面替换为现代化美化版本                 ║
echo ╚══════════════════════════════════════════════════╝
echo.

:: 检测 OpenManus-GUI 安装目录
set "GUI_DIR=E:\OpenManus\OpenManus-GUI"
if not exist "%GUI_DIR%" (
    echo [错误] 未找到 OpenManus-GUI 目录: %GUI_DIR%
    echo 请先运行 install_webui_windows.ps1 安装 Web UI 版。
    pause
    exit /b 1
)

:: 备份原版 app_ui.py
if exist "%GUI_DIR%\app_ui.py" (
    echo [1/3] 备份原版 app_ui.py ...
    copy /Y "%GUI_DIR%\app_ui.py" "%GUI_DIR%\app_ui_original.py" >nul
    echo       已备份为 app_ui_original.py
) else (
    echo [1/3] 未找到原版 app_ui.py，跳过备份。
)

:: 复制优化版
echo [2/3] 安装优化版 UI ...
copy /Y "%~dp0app_ui_enhanced.py" "%GUI_DIR%\app_ui.py" >nul
echo       已安装！

:: 完成
echo [3/3] 升级完成！
echo.
echo ╔══════════════════════════════════════════════════╗
echo ║   升级成功！请重新运行 启动WebUI.bat 查看效果    ║
echo ║                                                  ║
echo ║   如需恢复原版，运行以下命令：                   ║
echo ║   copy app_ui_original.py app_ui.py              ║
echo ╚══════════════════════════════════════════════════╝
echo.
pause
