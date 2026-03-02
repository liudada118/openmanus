#!/usr/bin/env python3
"""
OpenManus 模型切换工具
快速在不同 LLM 模型之间切换，无需手动编辑配置文件。
"""

import os
import sys
import re
from pathlib import Path

# ============================================================
# 预设模型配置
# ============================================================
MODELS = {
    "1": {
        "name": "GPT-4.1-mini",
        "model": "gpt-4.1-mini",
        "base_url": "https://api.openai.com/v1",
        "cost": "约 ¥0.14/次任务（最便宜）",
        "desc": "性价比之王，日常任务首选",
    },
    "2": {
        "name": "GPT-5.2",
        "model": "gpt-5.2",
        "base_url": "https://api.openai.com/v1",
        "cost": "约 ¥0.86/次任务",
        "desc": "最强模型，复杂任务/编码首选",
    },
    "3": {
        "name": "GPT-5-mini",
        "model": "gpt-5-mini",
        "base_url": "https://api.openai.com/v1",
        "cost": "约 ¥0.25/次任务",
        "desc": "性能与价格的平衡之选",
    },
    "4": {
        "name": "GPT-4.1",
        "model": "gpt-4.1",
        "base_url": "https://api.openai.com/v1",
        "cost": "约 ¥0.42/次任务",
        "desc": "全能型，长上下文支持好",
    },
    "5": {
        "name": "GPT-4.1-nano",
        "model": "gpt-4.1-nano",
        "base_url": "https://api.openai.com/v1",
        "cost": "约 ¥0.07/次任务（超便宜）",
        "desc": "极致省钱，简单任务可用",
    },
    "6": {
        "name": "Ollama 本地模型 (Qwen2.5 14B)",
        "model": "qwen2.5:14b",
        "base_url": "http://localhost:11434/v1",
        "cost": "完全免费（需本地 GPU）",
        "desc": "本地运行，需 RTX 5070 + Ollama",
    },
    "7": {
        "name": "Ollama 本地模型 (Llama 3.3 8B)",
        "model": "llama3.3:8b",
        "base_url": "http://localhost:11434/v1",
        "cost": "完全免费（需本地 GPU）",
        "desc": "本地运行，轻量级选择",
    },
    "8": {
        "name": "Ollama 本地模型 (DeepSeek-R1 14B)",
        "model": "deepseek-r1:14b",
        "base_url": "http://localhost:11434/v1",
        "cost": "完全免费（需本地 GPU）",
        "desc": "本地运行，推理能力强",
    },
}


def find_config() -> Path:
    """查找配置文件路径"""
    candidates = [
        Path(__file__).parent / "config" / "config.toml",
        Path.cwd() / "config" / "config.toml",
        Path.home() / "OpenManus" / "config" / "config.toml",
    ]
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]


def read_current_model(config_path: Path) -> str:
    """读取当前配置的模型名"""
    if not config_path.exists():
        return "未配置"
    content = config_path.read_text(encoding="utf-8")
    match = re.search(r'^\[llm\].*?^model\s*=\s*"([^"]+)"', content, re.MULTILINE | re.DOTALL)
    return match.group(1) if match else "未知"


def update_config(config_path: Path, model_info: dict, api_key: str = None):
    """更新配置文件中的模型设置"""
    if not config_path.exists():
        # 创建新配置
        config_path.parent.mkdir(parents=True, exist_ok=True)
        key = api_key or "sk-your-api-key-here"
        is_ollama = "localhost" in model_info["base_url"]
        if is_ollama:
            key = "ollama"

        content = f'''# ============================================================
# OpenManus 配置文件
# 当前模型: {model_info["name"]}
# ============================================================

# 主 LLM 配置
[llm]
model = "{model_info["model"]}"
base_url = "{model_info["base_url"]}"
api_key = "{key}"
max_tokens = 4096
temperature = 0.0

# 视觉模型配置
[llm.vision]
model = "{model_info["model"]}"
base_url = "{model_info["base_url"]}"
api_key = "{key}"
max_tokens = 4096
temperature = 0.0

# 浏览器配置
[browser]
headless = false
disable_security = true

# 搜索引擎配置
[search]
engine = "Google"
'''
        config_path.write_text(content, encoding="utf-8")
        return

    content = config_path.read_text(encoding="utf-8")

    # 更新 [llm] 部分的 model 和 base_url
    def replace_in_section(text, section, key, value):
        """在指定 section 中替换 key 的值"""
        pattern = rf'(\[{re.escape(section)}\].*?^{key}\s*=\s*)"[^"]*"'
        replacement = rf'\g<1>"{value}"'
        return re.sub(pattern, replacement, text, count=1, flags=re.MULTILINE | re.DOTALL)

    content = replace_in_section(content, "llm", "model", model_info["model"])
    content = replace_in_section(content, "llm", "base_url", model_info["base_url"])
    content = replace_in_section(content, "llm.vision", "model", model_info["model"])
    content = replace_in_section(content, "llm.vision", "base_url", model_info["base_url"])

    # 如果是 Ollama，更新 api_key
    is_ollama = "localhost" in model_info["base_url"]
    if is_ollama:
        content = replace_in_section(content, "llm", "api_key", "ollama")
        content = replace_in_section(content, "llm.vision", "api_key", "ollama")
    elif api_key:
        content = replace_in_section(content, "llm", "api_key", api_key)
        content = replace_in_section(content, "llm.vision", "api_key", api_key)

    # 更新注释中的模型名
    content = re.sub(
        r"# 当前模型:.*",
        f'# 当前模型: {model_info["name"]}',
        content,
    )
    content = re.sub(
        r"# 默认模型:.*",
        f'# 当前模型: {model_info["name"]}',
        content,
    )

    config_path.write_text(content, encoding="utf-8")


def main():
    config_path = find_config()
    current = read_current_model(config_path)

    print("=" * 60)
    print("  OpenManus 模型切换工具")
    print("=" * 60)
    print(f"\n  配置文件: {config_path}")
    print(f"  当前模型: {current}")
    print()
    print("-" * 60)
    print("  可选模型:")
    print("-" * 60)

    for key, info in MODELS.items():
        marker = " ◀ 当前" if info["model"] == current else ""
        print(f"  {key}) {info['name']}{marker}")
        print(f"     费用: {info['cost']}")
        print(f"     说明: {info['desc']}")
        print()

    print("-" * 60)
    print("  0) 自定义模型")
    print("  q) 退出")
    print("-" * 60)

    choice = input("\n请选择模型编号: ").strip()

    if choice.lower() == "q":
        print("已退出。")
        return

    if choice == "0":
        # 自定义模型
        print("\n--- 自定义模型配置 ---")
        model_name = input("模型名称 (如 gpt-4o): ").strip()
        base_url = input("API Base URL (如 https://api.openai.com/v1): ").strip()
        api_key = input("API Key: ").strip()

        if not model_name or not base_url:
            print("模型名称和 Base URL 不能为空！")
            return

        model_info = {
            "name": model_name,
            "model": model_name,
            "base_url": base_url,
        }
        update_config(config_path, model_info, api_key or None)
        print(f"\n✅ 已切换到自定义模型: {model_name}")
        return

    if choice not in MODELS:
        print("无效选择！")
        return

    model_info = MODELS[choice]

    # 如果是 Ollama 模型，提醒用户
    if "localhost" in model_info["base_url"]:
        print(f"\n⚠️  您选择了本地模型 {model_info['name']}")
        print("请确保已安装 Ollama 并下载了对应模型：")
        print(f"  1. 安装 Ollama: https://ollama.com/download")
        print(f"  2. 下载模型: ollama pull {model_info['model']}")
        confirm = input("\n确认切换? (y/N): ").strip().lower()
        if confirm != "y":
            print("已取消。")
            return

    update_config(config_path, model_info)
    print(f"\n✅ 已切换到: {model_info['name']}")
    print(f"   费用: {model_info['cost']}")
    print(f"\n现在可以运行 python main.py 启动 Agent 了！")


if __name__ == "__main__":
    main()
