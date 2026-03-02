# ============================================================
# OpenManus-GUI 一键安装脚本 (Windows)
# 安装带有 Gradio Web UI 界面的 OpenManus（含对话历史、多轮对话）
# ============================================================

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  OpenManus-GUI 一键安装脚本" -ForegroundColor Cyan
Write-Host "  Gradio Web UI + 对话历史 + 多轮对话 + 模型切换" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# --- 配置 ---
$INSTALL_DIR = "E:\OpenManus\OpenManus-GUI"
$REPO_URL = "https://github.com/Hank-Chromela/OpenManus-GUI.git"
$BRANCH = "main"

# --- 检查 Python ---
Write-Host "[1/7] 检查 Python 环境..." -ForegroundColor Yellow
$pythonCmd = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match "Python 3\.(1[0-2]|[0-9])") {
            $pythonCmd = $cmd
            Write-Host "  已找到: $ver" -ForegroundColor Green
            break
        }
    } catch {}
}
if (-not $pythonCmd) {
    Write-Host "  未找到 Python 3.10+！" -ForegroundColor Red
    Write-Host "  请从 https://www.python.org/downloads/ 下载安装" -ForegroundColor Red
    Write-Host "  安装时务必勾选 'Add Python to PATH'" -ForegroundColor Red
    pause
    exit 1
}

# --- 检查 Git ---
Write-Host "[2/7] 检查 Git 环境..." -ForegroundColor Yellow
try {
    $gitVer = git --version 2>&1
    Write-Host "  已找到: $gitVer" -ForegroundColor Green
} catch {
    Write-Host "  未找到 Git！" -ForegroundColor Red
    Write-Host "  请从 https://git-scm.com/download/win 下载安装" -ForegroundColor Red
    pause
    exit 1
}

# --- 安装 uv ---
Write-Host "[3/7] 检查 uv 包管理器..." -ForegroundColor Yellow
try {
    $uvVer = uv --version 2>&1
    Write-Host "  已找到: uv $uvVer" -ForegroundColor Green
} catch {
    Write-Host "  正在安装 uv..." -ForegroundColor Yellow
    Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
    $env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
}

# --- 克隆 OpenManus-GUI ---
Write-Host "[4/7] 克隆 OpenManus-GUI 项目..." -ForegroundColor Yellow
if (Test-Path $INSTALL_DIR) {
    Write-Host "  目录已存在: $INSTALL_DIR" -ForegroundColor Yellow
    $choice = Read-Host "  是否覆盖? (y/N)"
    if ($choice -ne "y" -and $choice -ne "Y") {
        Write-Host "  跳过克隆，使用已有文件。" -ForegroundColor Yellow
    } else {
        Remove-Item -Recurse -Force $INSTALL_DIR
        git clone -b $BRANCH $REPO_URL $INSTALL_DIR
    }
} else {
    git clone -b $BRANCH $REPO_URL $INSTALL_DIR
}
Set-Location $INSTALL_DIR

# --- 创建虚拟环境并安装依赖 ---
Write-Host "[5/7] 创建虚拟环境并安装依赖..." -ForegroundColor Yellow
if (-not (Test-Path ".venv")) {
    uv venv --python 3.12
}
& .venv\Scripts\activate.bat 2>$null
uv pip install -r requirements.txt
# 确保 Gradio 已安装（app_ui.py 需要）
uv pip install gradio
# 安装 Playwright 浏览器自动化工具
Write-Host "  安装 Playwright 浏览器..." -ForegroundColor Yellow
& .venv\Scripts\playwright.exe install chromium 2>$null

# --- 配置 API Key ---
Write-Host "[6/7] 配置 API Key 和模型..." -ForegroundColor Yellow
$configDir = "$INSTALL_DIR\config"
$configFile = "$configDir\config.toml"

if (-not (Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir -Force | Out-Null
}

if (-not (Test-Path $configFile)) {
    Write-Host ""
    Write-Host "  请输入您的 OpenAI API Key" -ForegroundColor Cyan
    Write-Host "  获取地址: https://platform.openai.com/api-keys" -ForegroundColor Cyan
    Write-Host "  (按回车跳过，稍后可手动编辑 config/config.toml)" -ForegroundColor Gray
    Write-Host ""
    $apiKey = Read-Host "  API Key"
    if ([string]::IsNullOrWhiteSpace($apiKey)) {
        $apiKey = "sk-your-api-key-here"
        Write-Host "  已跳过，请稍后编辑 config/config.toml 填入 API Key" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "  选择默认模型:" -ForegroundColor Cyan
    Write-Host "  1) GPT-4.1-mini  (最便宜, 推荐日常使用)" -ForegroundColor White
    Write-Host "  2) GPT-5.2       (最强, 复杂任务首选)" -ForegroundColor White
    Write-Host "  3) GPT-5-mini    (性价比平衡)" -ForegroundColor White
    Write-Host "  4) GPT-4.1       (全能型)" -ForegroundColor White
    $modelChoice = Read-Host "  请选择 (默认: 1)"

    switch ($modelChoice) {
        "2" { $model = "gpt-5.2"; $modelName = "GPT-5.2" }
        "3" { $model = "gpt-5-mini"; $modelName = "GPT-5-mini" }
        "4" { $model = "gpt-4.1"; $modelName = "GPT-4.1" }
        default { $model = "gpt-4.1-mini"; $modelName = "GPT-4.1-mini" }
    }

    $configContent = @"
# ============================================================
# OpenManus-GUI 配置文件
# 当前模型: $modelName
# ============================================================

# 主 LLM 配置
[llm]
model = "$model"
base_url = "https://api.openai.com/v1"
api_key = "$apiKey"
max_tokens = 4096
temperature = 0.0

# 视觉模型配置
[llm.vision]
model = "$model"
base_url = "https://api.openai.com/v1"
api_key = "$apiKey"
max_tokens = 4096
temperature = 0.0

# 浏览器配置
[browser]
headless = false
disable_security = true

# 搜索引擎配置
[search]
engine = "Google"
"@
    Set-Content -Path $configFile -Value $configContent -Encoding UTF8
    Write-Host "  配置已保存: $configFile" -ForegroundColor Green
} else {
    Write-Host "  配置文件已存在，跳过。" -ForegroundColor Green
}

# --- 复制模型切换工具并创建启动脚本 ---
Write-Host "[7/7] 创建启动脚本和工具..." -ForegroundColor Yellow

# 复制 switch_model.py
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$switchModelSrc = "$scriptDir\switch_model.py"
if (Test-Path $switchModelSrc) {
    Copy-Item $switchModelSrc "$INSTALL_DIR\switch_model.py" -Force
    Write-Host "  模型切换工具已复制。" -ForegroundColor Green
}

# 启动 Web UI (Gradio) 脚本
$startWebUI = @"
@echo off
chcp 65001 >nul
echo ============================================================
echo   OpenManus-GUI - AI Agent (Gradio Web UI)
echo   启动后自动打开浏览器: http://localhost:7860
echo ============================================================
echo.
cd /d "$INSTALL_DIR"
call .venv\Scripts\activate.bat

REM 显示当前模型
for /f "tokens=2 delims==" %%a in ('findstr /r "^model" config\config.toml 2^>nul') do (
    echo   当前模型: %%a
    goto :found_model
)
:found_model
echo.
echo [INFO] 正在启动 Gradio Web UI 服务...
echo [INFO] 浏览器将自动打开 http://localhost:7860
echo [INFO] 按 Ctrl+C 停止服务
echo.
python app_ui.py
pause
"@
Set-Content -Path "$INSTALL_DIR\启动WebUI.bat" -Value $startWebUI -Encoding UTF8

# 启动终端模式脚本
$startTerminal = @"
@echo off
chcp 65001 >nul
echo ============================================================
echo   OpenManus AI Agent - 终端模式
echo ============================================================
echo.
cd /d "$INSTALL_DIR"
call .venv\Scripts\activate.bat
python main.py
pause
"@
Set-Content -Path "$INSTALL_DIR\启动终端模式.bat" -Value $startTerminal -Encoding UTF8

# 启动 API 服务脚本
$startAPI = @"
@echo off
chcp 65001 >nul
echo ============================================================
echo   OpenManus-GUI - API Server (OpenAI 兼容)
echo   其他 UI 可通过 API 调用 Agent
echo ============================================================
echo.
cd /d "$INSTALL_DIR"
call .venv\Scripts\activate.bat
echo [INFO] 正在启动 API 服务...
python api_server.py
pause
"@
Set-Content -Path "$INSTALL_DIR\启动API服务.bat" -Value $startAPI -Encoding UTF8

# 切换模型脚本
$switchModel = @"
@echo off
chcp 65001 >nul
echo ============================================================
echo   OpenManus 模型切换工具
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
Write-Host "  安装完成！" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  安装目录: $INSTALL_DIR" -ForegroundColor White
Write-Host ""
Write-Host "  启动方式:" -ForegroundColor Cyan
Write-Host "    双击 '启动WebUI.bat'    -> Gradio Web 界面 (推荐)" -ForegroundColor White
Write-Host "    双击 '启动终端模式.bat'  -> 终端命令行模式" -ForegroundColor White
Write-Host "    双击 '启动API服务.bat'   -> OpenAI 兼容 API 服务" -ForegroundColor White
Write-Host ""
Write-Host "  工具:" -ForegroundColor Cyan
Write-Host "    双击 '切换模型.bat'      -> 切换 LLM 模型" -ForegroundColor White
Write-Host ""
Write-Host "  Web UI 功能:" -ForegroundColor Cyan
Write-Host "    - 对话历史记录（自动保存）" -ForegroundColor White
Write-Host "    - 多轮对话" -ForegroundColor White
Write-Host "    - 新建/重命名/删除会话" -ForegroundColor White
Write-Host "    - 实时查看 Agent 思考过程" -ForegroundColor White
Write-Host "    - 工作区文件管理" -ForegroundColor White
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
pause
