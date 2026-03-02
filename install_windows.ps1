#Requires -Version 5.1
<#
.SYNOPSIS
    OpenManus 本地 AI Agent 一键安装脚本 (Windows)
.DESCRIPTION
    自动安装 Python、uv、OpenManus 及其依赖，并生成配置文件。
    支持 GPT-5.2、GPT-4.1-mini、本地 Ollama 等多种模型。
.NOTES
    运行方式: 右键 -> 使用 PowerShell 运行
    或在 PowerShell 中执行: Set-ExecutionPolicy Bypass -Scope Process; .\install_windows.ps1
#>

$ErrorActionPreference = "Stop"

# ============================================================
# 颜色输出函数
# ============================================================
function Write-Step  { param($msg) Write-Host "`n[*] $msg" -ForegroundColor Cyan }
function Write-Ok    { param($msg) Write-Host "[+] $msg" -ForegroundColor Green }
function Write-Warn  { param($msg) Write-Host "[!] $msg" -ForegroundColor Yellow }
function Write-Err   { param($msg) Write-Host "[-] $msg" -ForegroundColor Red }

Write-Host @"
============================================================
   OpenManus 本地 AI Agent 一键安装脚本 (Windows)
   支持模型: GPT-5.2 / GPT-4.1-mini / Ollama 本地模型
============================================================
"@ -ForegroundColor Cyan

# ============================================================
# 1. 检查 Python
# ============================================================
Write-Step "检查 Python 环境..."
$pythonCmd = $null
foreach ($cmd in @("python", "python3")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match "Python 3\.(1[0-9]|[2-9][0-9])") {
            $pythonCmd = $cmd
            Write-Ok "找到 $ver"
            break
        }
    } catch {}
}

if (-not $pythonCmd) {
    Write-Err "未找到 Python 3.10+，请先安装 Python："
    Write-Host "  下载地址: https://www.python.org/downloads/"
    Write-Host "  安装时请勾选 'Add Python to PATH'"
    Read-Host "按回车退出"
    exit 1
}

# ============================================================
# 2. 安装 uv
# ============================================================
Write-Step "安装 uv (快速 Python 包管理器)..."
try {
    $uvVer = & uv --version 2>&1
    Write-Ok "uv 已安装: $uvVer"
} catch {
    Write-Warn "正在安装 uv..."
    Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
    # 刷新 PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    Write-Ok "uv 安装完成"
}

# ============================================================
# 3. 克隆 OpenManus
# ============================================================
$installDir = "$env:USERPROFILE\OpenManus"
Write-Step "克隆 OpenManus 到 $installDir ..."

if (Test-Path "$installDir\.git") {
    Write-Warn "OpenManus 目录已存在，正在更新..."
    Push-Location $installDir
    git pull
    Pop-Location
} else {
    if (Test-Path $installDir) { Remove-Item $installDir -Recurse -Force }
    git clone https://github.com/FoundationAgents/OpenManus.git $installDir
}
Write-Ok "OpenManus 代码就绪"

# ============================================================
# 4. 创建虚拟环境并安装依赖
# ============================================================
Write-Step "创建 Python 虚拟环境并安装依赖..."
Push-Location $installDir

uv venv --python 3.12
& .\.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt

Write-Ok "依赖安装完成"

# ============================================================
# 5. 安装 Playwright 浏览器
# ============================================================
Write-Step "安装 Playwright 浏览器 (用于网页自动化)..."
playwright install chromium
Write-Ok "Playwright 安装完成"

# ============================================================
# 6. 生成配置文件
# ============================================================
Write-Step "生成配置文件..."

$configDir = "$installDir\config"
if (-not (Test-Path $configDir)) { New-Item -ItemType Directory -Path $configDir | Out-Null }

# 询问 API Key
Write-Host ""
Write-Host "请输入您的 OpenAI API Key (从 https://platform.openai.com/api-keys 获取)" -ForegroundColor Yellow
Write-Host "如果暂时没有，直接按回车跳过（稍后可在配置文件中填写）" -ForegroundColor Gray
$apiKey = Read-Host "API Key"
if ([string]::IsNullOrWhiteSpace($apiKey)) { $apiKey = "sk-your-api-key-here" }

# 询问默认模型
Write-Host ""
Write-Host "选择默认模型:" -ForegroundColor Yellow
Write-Host "  1) GPT-4.1-mini  (推荐，便宜又好用，约 ¥0.14/次任务)"
Write-Host "  2) GPT-5.2       (最强，约 ¥0.86/次任务)"
Write-Host "  3) GPT-5-mini    (平衡，约 ¥0.25/次任务)"
$modelChoice = Read-Host "请输入数字 (默认 1)"

switch ($modelChoice) {
    "2" { $model = "gpt-5.2"; $modelDesc = "GPT-5.2" }
    "3" { $model = "gpt-5-mini"; $modelDesc = "GPT-5-mini" }
    default { $model = "gpt-4.1-mini"; $modelDesc = "GPT-4.1-mini" }
}

$configContent = @"
# ============================================================
# OpenManus 配置文件
# 默认模型: $modelDesc
# 生成时间: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
# ============================================================

# 主 LLM 配置 (Agent 的大脑)
[llm]
model = "$model"
base_url = "https://api.openai.com/v1"
api_key = "$apiKey"
max_tokens = 4096
temperature = 0.0

# 视觉模型配置 (用于理解图片/截图)
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

$configContent | Out-File -FilePath "$configDir\config.toml" -Encoding utf8
Write-Ok "配置文件已生成: $configDir\config.toml"

# ============================================================
# 7. 创建快捷启动脚本
# ============================================================
Write-Step "创建快捷启动脚本..."

# 主启动脚本
@"
@echo off
chcp 65001 >nul
echo ============================================================
echo   OpenManus AI Agent - 启动中...
echo   当前模型: $modelDesc
echo ============================================================
echo.
cd /d "$installDir"
call .venv\Scripts\activate.bat
python main.py
pause
"@ | Out-File -FilePath "$installDir\启动Agent.bat" -Encoding ascii

# 模型切换脚本
@"
@echo off
chcp 65001 >nul
echo ============================================================
echo   OpenManus 模型切换工具
echo ============================================================
echo.
cd /d "$installDir"
call .venv\Scripts\activate.bat
python switch_model.py
pause
"@ | Out-File -FilePath "$installDir\切换模型.bat" -Encoding ascii

Write-Ok "启动脚本已创建"

Pop-Location

# ============================================================
# 8. 完成
# ============================================================
Write-Host ""
Write-Host @"
============================================================
   安装完成！
============================================================

  安装目录: $installDir
  配置文件: $installDir\config\config.toml

  启动方式:
    方式1: 双击 "$installDir\启动Agent.bat"
    方式2: 打开终端，执行:
           cd $installDir
           .venv\Scripts\activate
           python main.py

  切换模型:
    双击 "$installDir\切换模型.bat"

  注意事项:
    - 首次使用前请确保 config.toml 中的 API Key 已填写
    - API Key 获取: https://platform.openai.com/api-keys
    - 新账户有 `$5 免费额度

============================================================
"@ -ForegroundColor Green

Read-Host "按回车退出"
