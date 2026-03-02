# ============================================================
# OpenManusWeb 一键安装脚本 (Windows)
# 安装带有 Web UI 界面的 OpenManus
# ============================================================

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  OpenManusWeb 一键安装脚本 (Web UI 版)" -ForegroundColor Cyan
Write-Host "  安装后可在浏览器中使用 AI Agent" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# --- 配置 ---
$INSTALL_DIR = "E:\OpenManus\OpenManusWeb"
$REPO_URL = "https://github.com/YunQiAI/OpenManusWeb.git"
$BRANCH = "dev_web_app"

# --- 检查 Python ---
Write-Host "[1/6] Checking Python..." -ForegroundColor Yellow
$pythonCmd = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match "Python 3\.(1[0-2]|[0-9])") {
            $pythonCmd = $cmd
            Write-Host "  Found: $ver" -ForegroundColor Green
            break
        }
    } catch {}
}
if (-not $pythonCmd) {
    Write-Host "  Python 3.10+ not found!" -ForegroundColor Red
    Write-Host "  Please install Python from https://www.python.org/downloads/" -ForegroundColor Red
    Write-Host "  IMPORTANT: Check 'Add Python to PATH' during installation!" -ForegroundColor Red
    pause
    exit 1
}

# --- 检查 Git ---
Write-Host "[2/6] Checking Git..." -ForegroundColor Yellow
try {
    $gitVer = git --version 2>&1
    Write-Host "  Found: $gitVer" -ForegroundColor Green
} catch {
    Write-Host "  Git not found!" -ForegroundColor Red
    Write-Host "  Please install Git from https://git-scm.com/download/win" -ForegroundColor Red
    pause
    exit 1
}

# --- 安装 uv ---
Write-Host "[3/6] Installing uv (fast package manager)..." -ForegroundColor Yellow
try {
    $uvVer = uv --version 2>&1
    Write-Host "  Found: uv $uvVer" -ForegroundColor Green
} catch {
    Write-Host "  Installing uv..." -ForegroundColor Yellow
    Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
    $env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
}

# --- 克隆 OpenManusWeb ---
Write-Host "[4/6] Cloning OpenManusWeb..." -ForegroundColor Yellow
if (Test-Path $INSTALL_DIR) {
    Write-Host "  Directory already exists: $INSTALL_DIR" -ForegroundColor Yellow
    $choice = Read-Host "  Overwrite? (y/N)"
    if ($choice -ne "y" -and $choice -ne "Y") {
        Write-Host "  Skipping clone, using existing files." -ForegroundColor Yellow
    } else {
        Remove-Item -Recurse -Force $INSTALL_DIR
        git clone -b $BRANCH $REPO_URL $INSTALL_DIR
    }
} else {
    git clone -b $BRANCH $REPO_URL $INSTALL_DIR
}
Set-Location $INSTALL_DIR

# --- 创建虚拟环境并安装依赖 ---
Write-Host "[5/6] Setting up virtual environment and dependencies..." -ForegroundColor Yellow
if (-not (Test-Path ".venv")) {
    uv venv --python 3.12
}
& .venv\Scripts\activate.bat 2>$null
uv pip install -r requirements.txt

# --- 配置 API Key ---
Write-Host "[6/6] Configuring API Key..." -ForegroundColor Yellow
$configDir = "$INSTALL_DIR\config"
$configFile = "$configDir\config.toml"

if (-not (Test-Path $configFile)) {
    Write-Host ""
    Write-Host "  Please enter your OpenAI API Key." -ForegroundColor Cyan
    Write-Host "  Get it from: https://platform.openai.com/api-keys" -ForegroundColor Cyan
    Write-Host "  (Press Enter to skip, you can set it later)" -ForegroundColor Gray
    Write-Host ""
    $apiKey = Read-Host "  API Key"
    if ([string]::IsNullOrWhiteSpace($apiKey)) {
        $apiKey = "sk-your-api-key-here"
        Write-Host "  Skipped. Please edit config/config.toml later." -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "  Select default model:" -ForegroundColor Cyan
    Write-Host "  1) GPT-4.1-mini  (cheapest, recommended)" -ForegroundColor White
    Write-Host "  2) GPT-5.2       (most powerful)" -ForegroundColor White
    Write-Host "  3) GPT-5-mini    (balanced)" -ForegroundColor White
    $modelChoice = Read-Host "  Choice (default: 1)"

    switch ($modelChoice) {
        "2" { $model = "gpt-5.2" }
        "3" { $model = "gpt-5-mini" }
        default { $model = "gpt-4.1-mini" }
    }

    $configContent = @"
# ============================================================
# OpenManusWeb Configuration
# Current Model: $model
# ============================================================

[llm]
model = "$model"
base_url = "https://api.openai.com/v1"
api_key = "$apiKey"
max_tokens = 4096
temperature = 0.0

[llm.vision]
model = "$model"
base_url = "https://api.openai.com/v1"
api_key = "$apiKey"
max_tokens = 4096
temperature = 0.0

[browser]
headless = false
disable_security = true

[search]
engine = "Google"
"@
    Set-Content -Path $configFile -Value $configContent -Encoding UTF8
    Write-Host "  Config saved: $configFile" -ForegroundColor Green
} else {
    Write-Host "  Config already exists, skipping." -ForegroundColor Green
}

# --- 复制模型切换工具 ---
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$switchModelSrc = "$scriptDir\switch_model.py"
if (Test-Path $switchModelSrc) {
    Copy-Item $switchModelSrc "$INSTALL_DIR\switch_model.py" -Force
    Write-Host "  Model switcher copied." -ForegroundColor Green
}

# --- 创建启动脚本 ---
$startWebUI = @"
@echo off
chcp 65001 >nul
echo ============================================================
echo   OpenManusWeb - AI Agent Web Interface
echo   Open browser: http://localhost:8000
echo ============================================================
echo.
cd /d "$INSTALL_DIR"
call .venv\Scripts\activate.bat
echo [INFO] Starting Web UI server...
echo [INFO] Please open http://localhost:8000 in your browser.
echo [INFO] Press Ctrl+C to stop the server.
echo.
python web_run.py
pause
"@
Set-Content -Path "$INSTALL_DIR\启动WebUI.bat" -Value $startWebUI -Encoding UTF8

$startTerminal = @"
@echo off
chcp 65001 >nul
echo ============================================================
echo   OpenManus AI Agent - Terminal Mode
echo ============================================================
echo.
cd /d "$INSTALL_DIR"
call .venv\Scripts\activate.bat
python main.py
pause
"@
Set-Content -Path "$INSTALL_DIR\启动终端模式.bat" -Value $startTerminal -Encoding UTF8

$switchModel = @"
@echo off
chcp 65001 >nul
echo ============================================================
echo   OpenManus Model Switcher
echo ============================================================
echo.
cd /d "$INSTALL_DIR"
call .venv\Scripts\activate.bat
python switch_model.py
pause
"@
Set-Content -Path "$INSTALL_DIR\切换模型.bat" -Value $switchModel -Encoding UTF8

# --- 完成 ---
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Install directory: $INSTALL_DIR" -ForegroundColor White
Write-Host ""
Write-Host "  How to use:" -ForegroundColor Cyan
Write-Host "    1. Double-click '启动WebUI.bat' to start Web UI" -ForegroundColor White
Write-Host "    2. Open http://localhost:8000 in your browser" -ForegroundColor White
Write-Host "    3. Start chatting with your AI Agent!" -ForegroundColor White
Write-Host ""
Write-Host "  Other tools:" -ForegroundColor Cyan
Write-Host "    - '启动终端模式.bat' : Terminal mode (classic)" -ForegroundColor White
Write-Host "    - '切换模型.bat'     : Switch LLM model" -ForegroundColor White
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
pause
