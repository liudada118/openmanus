#!/usr/bin/env bash
# ============================================================
# OpenManus 本地 AI Agent 一键安装脚本 (Linux / macOS)
# 支持模型: GPT-5.2 / GPT-4.1-mini / Ollama 本地模型
# 运行方式: chmod +x install_unix.sh && ./install_unix.sh
# ============================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

step()  { echo -e "\n${CYAN}[*] $1${NC}"; }
ok()    { echo -e "${GREEN}[+] $1${NC}"; }
warn()  { echo -e "${YELLOW}[!] $1${NC}"; }
err()   { echo -e "${RED}[-] $1${NC}"; }

echo -e "${CYAN}"
echo "============================================================"
echo "   OpenManus 本地 AI Agent 一键安装脚本 (Linux / macOS)"
echo "   支持模型: GPT-5.2 / GPT-4.1-mini / Ollama 本地模型"
echo "============================================================"
echo -e "${NC}"

# ============================================================
# 1. 检查 Python
# ============================================================
step "检查 Python 环境..."
PYTHON_CMD=""
for cmd in python3.12 python3.11 python3; do
    if command -v "$cmd" &>/dev/null; then
        ver=$($cmd --version 2>&1)
        if echo "$ver" | grep -qE "Python 3\.(1[0-9]|[2-9][0-9])"; then
            PYTHON_CMD="$cmd"
            ok "找到 $ver"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    err "未找到 Python 3.10+，请先安装："
    echo "  macOS:  brew install python@3.12"
    echo "  Ubuntu: sudo apt install python3.12 python3.12-venv"
    exit 1
fi

# ============================================================
# 2. 安装 uv
# ============================================================
step "安装 uv (快速 Python 包管理器)..."
if command -v uv &>/dev/null; then
    ok "uv 已安装: $(uv --version)"
else
    warn "正在安装 uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
    ok "uv 安装完成"
fi

# ============================================================
# 3. 克隆 OpenManus
# ============================================================
INSTALL_DIR="$HOME/OpenManus"
step "克隆 OpenManus 到 $INSTALL_DIR ..."

if [ -d "$INSTALL_DIR/.git" ]; then
    warn "OpenManus 目录已存在，正在更新..."
    cd "$INSTALL_DIR"
    git pull
else
    [ -d "$INSTALL_DIR" ] && rm -rf "$INSTALL_DIR"
    git clone https://github.com/FoundationAgents/OpenManus.git "$INSTALL_DIR"
fi
ok "OpenManus 代码就绪"

# ============================================================
# 4. 创建虚拟环境并安装依赖
# ============================================================
step "创建 Python 虚拟环境并安装依赖..."
cd "$INSTALL_DIR"

uv venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt

ok "依赖安装完成"

# ============================================================
# 5. 安装 Playwright 浏览器
# ============================================================
step "安装 Playwright 浏览器 (用于网页自动化)..."
playwright install chromium
ok "Playwright 安装完成"

# ============================================================
# 6. 生成配置文件
# ============================================================
step "生成配置文件..."

mkdir -p "$INSTALL_DIR/config"

echo ""
echo -e "${YELLOW}请输入您的 OpenAI API Key (从 https://platform.openai.com/api-keys 获取)${NC}"
echo -e "如果暂时没有，直接按回车跳过（稍后可在配置文件中填写）"
read -rp "API Key: " API_KEY
[ -z "$API_KEY" ] && API_KEY="sk-your-api-key-here"

echo ""
echo -e "${YELLOW}选择默认模型:${NC}"
echo "  1) GPT-4.1-mini  (推荐，便宜又好用，约 ¥0.14/次任务)"
echo "  2) GPT-5.2       (最强，约 ¥0.86/次任务)"
echo "  3) GPT-5-mini    (平衡，约 ¥0.25/次任务)"
read -rp "请输入数字 (默认 1): " MODEL_CHOICE

case "$MODEL_CHOICE" in
    2) MODEL="gpt-5.2"; MODEL_DESC="GPT-5.2" ;;
    3) MODEL="gpt-5-mini"; MODEL_DESC="GPT-5-mini" ;;
    *) MODEL="gpt-4.1-mini"; MODEL_DESC="GPT-4.1-mini" ;;
esac

cat > "$INSTALL_DIR/config/config.toml" << EOF
# ============================================================
# OpenManus 配置文件
# 默认模型: $MODEL_DESC
# 生成时间: $(date '+%Y-%m-%d %H:%M:%S')
# ============================================================

# 主 LLM 配置 (Agent 的大脑)
[llm]
model = "$MODEL"
base_url = "https://api.openai.com/v1"
api_key = "$API_KEY"
max_tokens = 4096
temperature = 0.0

# 视觉模型配置 (用于理解图片/截图)
[llm.vision]
model = "$MODEL"
base_url = "https://api.openai.com/v1"
api_key = "$API_KEY"
max_tokens = 4096
temperature = 0.0

# 浏览器配置
[browser]
headless = false
disable_security = true

# 搜索引擎配置
[search]
engine = "Google"
EOF

ok "配置文件已生成: $INSTALL_DIR/config/config.toml"

# ============================================================
# 7. 创建快捷启动脚本
# ============================================================
step "创建快捷启动脚本..."

cat > "$INSTALL_DIR/start.sh" << 'SCRIPT'
#!/usr/bin/env bash
cd "$(dirname "$0")"
source .venv/bin/activate
echo "============================================================"
echo "  OpenManus AI Agent - 启动中..."
grep '^model' config/config.toml | head -1
echo "============================================================"
echo ""
python main.py
SCRIPT
chmod +x "$INSTALL_DIR/start.sh"

ok "启动脚本已创建"

# ============================================================
# 8. 完成
# ============================================================
echo ""
echo -e "${GREEN}"
echo "============================================================"
echo "   安装完成！"
echo "============================================================"
echo ""
echo "  安装目录: $INSTALL_DIR"
echo "  配置文件: $INSTALL_DIR/config/config.toml"
echo ""
echo "  启动方式:"
echo "    方式1: $INSTALL_DIR/start.sh"
echo "    方式2: cd $INSTALL_DIR && source .venv/bin/activate && python main.py"
echo ""
echo "  切换模型:"
echo "    cd $INSTALL_DIR && source .venv/bin/activate && python switch_model.py"
echo ""
echo "  注意事项:"
echo "    - 首次使用前请确保 config.toml 中的 API Key 已填写"
echo "    - API Key 获取: https://platform.openai.com/api-keys"
echo "    - 新账户有 \$5 免费额度"
echo ""
echo "============================================================"
echo -e "${NC}"
