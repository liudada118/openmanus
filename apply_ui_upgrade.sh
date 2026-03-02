#!/bin/bash
# OpenManus UI 界面升级脚本 (macOS / Linux)

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║          OpenManus UI 界面升级工具               ║"
echo "║   将默认界面替换为现代化美化版本                 ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# 检测 OpenManus-GUI 安装目录
GUI_DIR="$HOME/OpenManus-GUI"
if [ ! -d "$GUI_DIR" ]; then
    GUI_DIR="$HOME/OpenManus/OpenManus-GUI"
fi
if [ ! -d "$GUI_DIR" ]; then
    echo "[错误] 未找到 OpenManus-GUI 目录"
    echo "请先运行 install_webui_unix.sh 安装 Web UI 版。"
    exit 1
fi

# 备份原版
if [ -f "$GUI_DIR/app_ui.py" ]; then
    echo "[1/3] 备份原版 app_ui.py ..."
    cp "$GUI_DIR/app_ui.py" "$GUI_DIR/app_ui_original.py"
    echo "      已备份为 app_ui_original.py"
else
    echo "[1/3] 未找到原版 app_ui.py，跳过备份。"
fi

# 复制优化版
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "[2/3] 安装优化版 UI ..."
cp "$SCRIPT_DIR/app_ui_enhanced.py" "$GUI_DIR/app_ui.py"
echo "      已安装！"

# 完成
echo "[3/3] 升级完成！"
echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║   升级成功！请重新运行启动脚本查看效果           ║"
echo "║                                                  ║"
echo "║   如需恢复原版：                                 ║"
echo "║   cp app_ui_original.py app_ui.py                ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""
