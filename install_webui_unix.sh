#!/bin/bash
# ============================================================
# OpenManus-GUI 一键安装脚本 (macOS / Linux)
# 安装带有 Gradio Web UI 界面的 OpenManus（含对话历史、多轮对话）
# ============================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}============================================================${NC}"
echo -e "${CYAN}  OpenManus-GUI 一键安装脚本${NC}"
echo -e "${CYAN}  Gradio Web UI + 对话历史 + 多轮对话 + 模型切换${NC}"
echo -e "${CYAN}============================================================${NC}"
echo ""

# --- 配置 ---
INSTALL_DIR="$HOME/OpenManus-GUI"
REPO_URL="https://github.com/Hank-Chromela/OpenManus-GUI.git"
BRANCH="main"

# --- 检查 Python ---
echo -e "${YELLOW}[1/7] 检查 Python 环境...${NC}"
PYTHON_CMD=""
for cmd in python3.12 python3.11 python3.10 python3 python; do
    if command -v $cmd &>/dev/null; then
        ver=$($cmd --version 2>&1)
        if echo "$ver" | grep -qE "Python 3\.(1[0-2]|[0-9])"; then
            PYTHON_CMD=$cmd
            echo -e "  ${GREEN}已找到: $ver${NC}"
            break
        fi
    fi
done
if [ -z "$PYTHON_CMD" ]; then
    echo -e "  ${RED}未找到 Python 3.10+！${NC}"
    echo -e "  ${RED}请安装 Python: https://www.python.org/downloads/${NC}"
    exit 1
fi

# --- 检查 Git ---
echo -e "${YELLOW}[2/7] 检查 Git 环境...${NC}"
if command -v git &>/dev/null; then
    echo -e "  ${GREEN}已找到: $(git --version)${NC}"
else
    echo -e "  ${RED}未找到 Git！请先安装 Git。${NC}"
    exit 1
fi

# --- 安装 uv ---
echo -e "${YELLOW}[3/7] 检查 uv 包管理器...${NC}"
if command -v uv &>/dev/null; then
    echo -e "  ${GREEN}已找到: $(uv --version)${NC}"
else
    echo -e "  ${YELLOW}正在安装 uv...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# --- 克隆项目 ---
echo -e "${YELLOW}[4/7] 克隆 OpenManus-GUI 项目...${NC}"
if [ -d "$INSTALL_DIR" ]; then
    echo -e "  ${YELLOW}目录已存在: $INSTALL_DIR${NC}"
    read -p "  是否覆盖? (y/N): " choice
    if [ "$choice" = "y" ] || [ "$choice" = "Y" ]; then
        rm -rf "$INSTALL_DIR"
        git clone -b "$BRANCH" "$REPO_URL" "$INSTALL_DIR"
    else
        echo -e "  ${YELLOW}跳过克隆，使用已有文件。${NC}"
    fi
else
    git clone -b "$BRANCH" "$REPO_URL" "$INSTALL_DIR"
fi
cd "$INSTALL_DIR"

# --- 创建虚拟环境并安装依赖 ---
echo -e "${YELLOW}[5/7] 创建虚拟环境并安装依赖...${NC}"
if [ ! -d ".venv" ]; then
    uv venv --python 3.12
fi
source .venv/bin/activate
uv pip install -r requirements.txt
uv pip install gradio
echo -e "  ${YELLOW}安装 Playwright 浏览器...${NC}"
playwright install chromium 2>/dev/null || true

# --- 配置 API Key ---
echo -e "${YELLOW}[6/7] 配置 API Key 和模型...${NC}"
CONFIG_DIR="$INSTALL_DIR/config"
CONFIG_FILE="$CONFIG_DIR/config.toml"

mkdir -p "$CONFIG_DIR"

if [ ! -f "$CONFIG_FILE" ]; then
    echo ""
    echo -e "  ${CYAN}请输入您的 OpenAI API Key${NC}"
    echo -e "  ${CYAN}获取地址: https://platform.openai.com/api-keys${NC}"
    echo -e "  (按回车跳过，稍后可手动编辑 config/config.toml)"
    echo ""
    read -p "  API Key: " API_KEY
    if [ -z "$API_KEY" ]; then
        API_KEY="sk-your-api-key-here"
        echo -e "  ${YELLOW}已跳过，请稍后编辑 config/config.toml 填入 API Key${NC}"
    fi

    echo ""
    echo -e "  ${CYAN}选择默认模型:${NC}"
    echo "  1) GPT-4.1-mini  (最便宜, 推荐日常使用)"
    echo "  2) GPT-5.2       (最强, 复杂任务首选)"
    echo "  3) GPT-5-mini    (性价比平衡)"
    echo "  4) GPT-4.1       (全能型)"
    read -p "  请选择 (默认: 1): " MODEL_CHOICE

    case $MODEL_CHOICE in
        2) MODEL="gpt-5.2"; MODEL_NAME="GPT-5.2" ;;
        3) MODEL="gpt-5-mini"; MODEL_NAME="GPT-5-mini" ;;
        4) MODEL="gpt-4.1"; MODEL_NAME="GPT-4.1" ;;
        *) MODEL="gpt-4.1-mini"; MODEL_NAME="GPT-4.1-mini" ;;
    esac

    cat > "$CONFIG_FILE" << EOF
# ============================================================
# OpenManus-GUI 配置文件
# 当前模型: $MODEL_NAME
# ============================================================

# 主 LLM 配置
[llm]
model = "$MODEL"
base_url = "https://api.openai.com/v1"
api_key = "$API_KEY"
max_tokens = 4096
temperature = 0.0

# 视觉模型配置
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
    echo -e "  ${GREEN}配置已保存: $CONFIG_FILE${NC}"
else
    echo -e "  ${GREEN}配置文件已存在，跳过。${NC}"
fi

# --- 复制工具并创建启动脚本 ---
echo -e "${YELLOW}[7/7] 创建启动脚本和工具...${NC}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$SCRIPT_DIR/switch_model.py" ]; then
    cp "$SCRIPT_DIR/switch_model.py" "$INSTALL_DIR/switch_model.py"
    echo -e "  ${GREEN}模型切换工具已复制。${NC}"
fi

# 启动 Web UI 脚本
cat > "$INSTALL_DIR/start_webui.sh" << 'SCRIPT'
#!/bin/bash
cd "$(dirname "$0")"
source .venv/bin/activate
echo "============================================================"
echo "  OpenManus-GUI - AI Agent (Gradio Web UI)"
echo "  浏览器将自动打开: http://localhost:7860"
echo "============================================================"
echo ""
echo "  当前模型: $(grep '^model' config/config.toml 2>/dev/null | head -1 | cut -d'"' -f2)"
echo ""
python app_ui.py
SCRIPT
chmod +x "$INSTALL_DIR/start_webui.sh"

# 启动终端模式脚本
cat > "$INSTALL_DIR/start_terminal.sh" << 'SCRIPT'
#!/bin/bash
cd "$(dirname "$0")"
source .venv/bin/activate
echo "============================================================"
echo "  OpenManus AI Agent - 终端模式"
echo "============================================================"
echo ""
python main.py
SCRIPT
chmod +x "$INSTALL_DIR/start_terminal.sh"

# 切换模型脚本
cat > "$INSTALL_DIR/switch_model.sh" << 'SCRIPT'
#!/bin/bash
cd "$(dirname "$0")"
source .venv/bin/activate
python switch_model.py
SCRIPT
chmod +x "$INSTALL_DIR/switch_model.sh"

# --- 完成 ---
echo ""
echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}  安装完成！${NC}"
echo -e "${GREEN}============================================================${NC}"
echo ""
echo -e "  安装目录: $INSTALL_DIR"
echo ""
echo -e "  ${CYAN}启动方式:${NC}"
echo "    ./start_webui.sh     -> Gradio Web 界面 (推荐)"
echo "    ./start_terminal.sh  -> 终端命令行模式"
echo ""
echo -e "  ${CYAN}工具:${NC}"
echo "    ./switch_model.sh    -> 切换 LLM 模型"
echo ""
echo -e "  ${CYAN}Web UI 功能:${NC}"
echo "    - 对话历史记录（自动保存）"
echo "    - 多轮对话"
echo "    - 新建/重命名/删除会话"
echo "    - 实时查看 Agent 思考过程"
echo ""
echo -e "${GREEN}============================================================${NC}"
