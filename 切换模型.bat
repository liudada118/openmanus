@echo off
chcp 65001 >nul
echo ============================================================
echo   OpenManus Model Switcher
echo ============================================================
echo.

REM --- Detect OpenManus installation directory ---
set "OPENMANUS_DIR=%~dp0"
if exist "%OPENMANUS_DIR%switch_model.py" (
    cd /d "%OPENMANUS_DIR%"
    goto :found
)
set "OPENMANUS_DIR=%USERPROFILE%\OpenManus"
if exist "%OPENMANUS_DIR%\switch_model.py" (
    cd /d "%OPENMANUS_DIR%"
    goto :found
)
set "OPENMANUS_DIR=D:\OpenManus"
if exist "%OPENMANUS_DIR%\switch_model.py" (
    cd /d "%OPENMANUS_DIR%"
    goto :found
)
echo [ERROR] Cannot find switch_model.py!
echo Please place this file in your OpenManus folder.
pause
exit /b 1

:found
REM --- Activate virtual environment ---
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo [ERROR] Virtual environment not found!
    pause
    exit /b 1
)

python switch_model.py
pause
