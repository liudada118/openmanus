#!/bin/bash
# ============================================================
# OpenManusWeb 一键安装脚本 (macOS / Linux)
# 安装带有 Web UI 界面的 OpenManus
# ============================================================

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

INSTALL_DIR="$HOME/OpenManusWeb"
REPO_URL="https://github.com/YunQiAI/OpenManusWeb.git"
BRANCH="dev_web_app"

echo -e "${CYAN}============================================================${NC}"
echo -e "${CYAN}  OpenManusWeb 一键安装脚本 (Web UI 版)${NC}"
echo -e "${CYAN}  安装后可在浏览器中使用 AI Agent${NC}"
echo -e "${CYAN}============================================================${NC}"
echo ""

# --- 检查 Python ---
echo -e "${YELLOW}[1/6] Checking Python...${NC}"
PYTHON_CMD=""
for cmd in python3 python; do
    if command -v $cmd &>/dev/null; then
        ver=$($cmd --version 2>&1)
        if echo "$ver" | grep -qE "Python 3\.(1[0-2]|[0-9])"; then
            PYTHON_CMD=$cmd
            echo -e "  ${GREEN}Found: $ver${NC}"
            break
        fi
    fi
done
if [ -z "$PYTHON_CMD" ]; then
    echo -e "  ${RED}Python 3.10+ not found!${NC}"
    echo -e "  ${RED}Please install Python: https://www.python.org/downloads/${NC}"
    exit 1
fi

# --- 检查 Git ---
echo -e "${YELLOW}[2/6] Checking Git...${NC}"
if command -v git &>/dev/null; then
    echo -e "  ${GREEN}Found: $(git --version)${NC}"
else
    echo -e "  ${RED}Git not found! Please install Git first.${NC}"
    exit 1
fi

# --- 安装 uv ---
echo -e "${YELLOW}[3/6] Installing uv (fast package manager)...${NC}"
if command -v uv &>/dev/null; then
    echo -e "  ${GREEN}Found: uv $(uv --version)${NC}"
else
    echo -e "  Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# --- 克隆 OpenManusWeb ---
echo -e "${YELLOW}[4/6] Cloning OpenManusWeb...${NC}"
if [ -d "$INSTALL_DIR" ]; then
    echo -e "  ${YELLOW}Directory already exists: $INSTALL_DIR${NC}"
    read -p "  Overwrite? (y/N): " choice
    if [ "$choice" = "y" ] || [ "$choice" = "Y" ]; then
        rm -rf "$INSTALL_DIR"
        git clone -b "$BRANCH" "$REPO_URL" "$INSTALL_DIR"
    else
        echo -e "  Skipping clone, using existing files."
    fi
else
    git clone -b "$BRANCH" "$REPO_URL" "$INSTALL_DIR"
fi
cd "$INSTALL_DIR"

# --- 创建虚拟环境并安装依赖 ---
echo -e "${YELLOW}[5/6] Setting up virtual environment and dependencies...${NC}"
if [ ! -d ".venv" ]; then
    uv venv --python 3.12
fi
source .venv/bin/activate
uv pip install -r requirements.txt

# --- 配置 API Key ---
echo -e "${YELLOW}[6/6] Configuring API Key...${NC}"
CONFIG_FILE="$INSTALL_DIR/config/config.toml"

if [ ! -f "$CONFIG_FILE" ]; then
    echo ""
    echo -e "  ${CYAN}Please enter your OpenAI API Key.${NC}"
    echo -e "  Get it from: https://platform.openai.com/api-keys"
    echo -e "  (Press Enter to skip, you can set it later)"
    echo ""
    read -p "  API Key: " API_KEY
    if [ -z "$API_KEY" ]; then
        API_KEY="sk-your-api-key-here"
        echo -e "  ${YELLOW}Skipped. Please edit config/config.toml later.${NC}"
    fi

    echo ""
    echo -e "  ${CYAN}Select default model:${NC}"
    echo "  1) GPT-4.1-mini  (cheapest, recommended)"
    echo "  2) GPT-5.2       (most powerful)"
    echo "  3) GPT-5-mini    (balanced)"
    read -p "  Choice (default: 1): " MODEL_CHOICE

    case "$MODEL_CHOICE" in
        2) MODEL="gpt-5.2" ;;
        3) MODEL="gpt-5-mini" ;;
        *) MODEL="gpt-4.1-mini" ;;
    esac

    cat > "$CONFIG_FILE" << EOF
# ============================================================
# OpenManusWeb Configuration
# Current Model: $MODEL
# ============================================================

[llm]
model = "$MODEL"
base_url = "https://api.openai.com/v1"
api_key = "$API_KEY"
max_tokens = 4096
temperature = 0.0

[llm.vision]
model = "$MODEL"
base_url = "https://api.openai.com/v1"
api_key = "$API_KEY"
max_tokens = 4096
temperature = 0.0

[browser]
headless = false
disable_security = true

[search]
engine = "Google"
EOF
    echo -e "  ${GREEN}Config saved: $CONFIG_FILE${NC}"
else
    echo -e "  ${GREEN}Config already exists, skipping.${NC}"
fi

# --- 复制模型切换工具 ---
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$SCRIPT_DIR/switch_model.py" ]; then
    cp "$SCRIPT_DIR/switch_model.py" "$INSTALL_DIR/switch_model.py"
    echo -e "  ${GREEN}Model switcher copied.${NC}"
fi

# --- 创建启动脚本 ---
cat > "$INSTALL_DIR/start_webui.sh" << 'SCRIPT'
#!/bin/bash
echo "============================================================"
echo "  OpenManusWeb - AI Agent Web Interface"
echo "  Open browser: http://localhost:8000"
echo "============================================================"
echo ""
cd "$(dirname "$0")"
source .venv/bin/activate
echo "[INFO] Starting Web UI server..."
echo "[INFO] Please open http://localhost:8000 in your browser."
echo "[INFO] Press Ctrl+C to stop the server."
echo ""
python web_run.py
SCRIPT
chmod +x "$INSTALL_DIR/start_webui.sh"

cat > "$INSTALL_DIR/start_terminal.sh" << 'SCRIPT'
#!/bin/bash
echo "============================================================"
echo "  OpenManus AI Agent - Terminal Mode"
echo "============================================================"
echo ""
cd "$(dirname "$0")"
source .venv/bin/activate
python main.py
SCRIPT
chmod +x "$INSTALL_DIR/start_terminal.sh"

# --- 完成 ---
echo ""
echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}  Installation Complete!${NC}"
echo -e "${GREEN}============================================================${NC}"
echo ""
echo -e "  Install directory: $INSTALL_DIR"
echo ""
echo -e "  ${CYAN}How to use:${NC}"
echo "    1. Run: cd $INSTALL_DIR && ./start_webui.sh"
echo "    2. Open http://localhost:8000 in your browser"
echo "    3. Start chatting with your AI Agent!"
echo ""
echo -e "  ${CYAN}Other tools:${NC}"
echo "    - ./start_terminal.sh  : Terminal mode (classic)"
echo "    - python switch_model.py : Switch LLM model"
echo ""
echo -e "${GREEN}============================================================${NC}"
