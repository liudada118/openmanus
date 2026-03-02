# app_ui_enhanced.py - Manus-Style Gradio UI
# 模仿 Manus 官方界面风格：白色极简 + 左侧任务列表 + 右侧对话区
# 用法：将此文件复制到 OpenManus-GUI 目录并重命名为 app_ui.py

import gradio as gr
import asyncio
import datetime
import os
import json
import re
import webbrowser
import threading
from pathlib import Path
from typing import Dict, List, Optional

# Assuming app structure is accessible
from app.agent.manus import Manus
from app.logger import logger
from app.schema import AgentState, Message as AgentMessage, Memory

# --- Constants ---
HISTORY_DIR = Path("chatsHistory")
UI_HOST = "127.0.0.1"
UI_PORT = 7860
UI_BASE_URL = f"http://{UI_HOST}:{UI_PORT}"

# --- Read current model from config ---
def get_current_model():
    """读取 config.toml 获取当前使用的模型名称"""
    config_paths = [
        Path("config/config.toml"),
        Path("../config/config.toml"),
    ]
    for config_path in config_paths:
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    model_match = re.search(r'model\s*=\s*"([^"]+)"', content)
                    if model_match:
                        return model_match.group(1)
            except Exception:
                pass
    return "未知模型"

CURRENT_MODEL = get_current_model()

# ============================================================
# Manus 风格 CSS - 白色极简主题
# ============================================================
CUSTOM_CSS = """
/* ===== 全局重置 ===== */
.gradio-container {
    max-width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
    background: #ffffff !important;
}

body, .main, .app {
    background: #ffffff !important;
}

/* 隐藏 Gradio 默认 footer */
footer { display: none !important; }

/* ===== 顶部导航栏 ===== */
.top-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 24px;
    border-bottom: 1px solid #f0f0f0;
    background: #ffffff;
    position: sticky;
    top: 0;
    z-index: 100;
}

.top-nav-left {
    display: flex;
    align-items: center;
    gap: 12px;
}

.top-nav-logo {
    font-size: 18px;
    font-weight: 700;
    color: #1a1a1a;
    letter-spacing: -0.3px;
}

.top-nav-logo span {
    color: #6366f1;
}

.top-nav-model {
    font-size: 12px;
    color: #8b8b8b;
    background: #f5f5f5;
    padding: 4px 10px;
    border-radius: 12px;
    font-weight: 500;
}

.top-nav-right {
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ===== 左侧边栏 ===== */
.sidebar-wrapper {
    background: #fafafa !important;
    border-right: 1px solid #f0f0f0;
    height: calc(100vh - 53px);
    overflow-y: auto;
    padding: 0 !important;
}

.sidebar-header {
    padding: 16px 16px 8px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.sidebar-title {
    font-size: 13px;
    font-weight: 600;
    color: #8b8b8b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* 新建任务按钮 - Manus 风格 */
.new-task-btn {
    background: #ffffff !important;
    color: #1a1a1a !important;
    border: 1px solid #e5e5e5 !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    padding: 10px 16px !important;
    margin: 12px 16px !important;
    transition: all 0.15s ease !important;
    box-shadow: none !important;
    width: calc(100% - 32px) !important;
}

.new-task-btn:hover {
    background: #f5f5f5 !important;
    border-color: #d0d0d0 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
}

/* 会话列表 */
.session-list .wrap {
    gap: 2px !important;
    padding: 0 8px !important;
}

.session-list label {
    border-radius: 8px !important;
    padding: 10px 12px !important;
    margin: 1px 0 !important;
    transition: all 0.15s ease !important;
    border: none !important;
    background: transparent !important;
    font-size: 14px !important;
    color: #4a4a4a !important;
    cursor: pointer !important;
}

.session-list label:hover {
    background: #f0f0f0 !important;
}

.session-list label.selected {
    background: #f0f0f0 !important;
    font-weight: 600 !important;
    color: #1a1a1a !important;
}

/* 会话管理区域 */
.manage-section {
    padding: 12px 16px;
    border-top: 1px solid #f0f0f0;
    margin-top: 8px;
}

.manage-label {
    font-size: 12px;
    color: #8b8b8b;
    font-weight: 500;
    margin-bottom: 6px;
}

.manage-btn {
    border-radius: 6px !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    padding: 6px 12px !important;
    border: 1px solid #e5e5e5 !important;
    background: #ffffff !important;
    color: #4a4a4a !important;
    transition: all 0.15s ease !important;
}

.manage-btn:hover {
    background: #f5f5f5 !important;
}

.delete-btn {
    border-color: #fecaca !important;
    color: #dc2626 !important;
}

.delete-btn:hover {
    background: #fef2f2 !important;
}

/* ===== 右侧主区域 ===== */
.main-area {
    background: #ffffff !important;
    height: calc(100vh - 53px);
    display: flex;
    flex-direction: column;
}

/* 聊天区域 */
.chat-area {
    border: none !important;
    box-shadow: none !important;
    border-radius: 0 !important;
    background: #ffffff !important;
}

.chat-area .wrapper {
    padding: 0 !important;
}

/* 聊天气泡 - Manus 风格 */
.chatbot {
    background: #ffffff !important;
}

.chatbot .message-wrap {
    padding: 8px 24px !important;
}

.chatbot .message-wrap .message {
    border-radius: 12px !important;
    padding: 14px 18px !important;
    font-size: 14px !important;
    line-height: 1.7 !important;
    max-width: 85% !important;
}

/* 用户消息 - 浅灰背景 */
.chatbot .message-wrap .message.user {
    background: #f5f5f5 !important;
    color: #1a1a1a !important;
    border: none !important;
    border-radius: 16px 16px 4px 16px !important;
}

/* AI 消息 - 白色背景 */
.chatbot .message-wrap .message.bot {
    background: #ffffff !important;
    color: #1a1a1a !important;
    border: 1px solid #f0f0f0 !important;
    border-radius: 16px 16px 16px 4px !important;
}

/* Agent 思考步骤标签 - 模仿 Manus 的 pill badges */
.chatbot .message-wrap .message.bot .step-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #f5f5f5;
    border-radius: 20px;
    padding: 5px 12px;
    font-size: 13px;
    color: #4a4a4a;
    margin: 3px 0;
}

.chatbot .message-wrap .message.bot .step-badge .step-icon {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: #6366f1;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 10px;
}

/* ===== 底部输入区域 - Manus 风格 ===== */
.input-area {
    padding: 16px 24px 20px 24px;
    background: #ffffff;
    border-top: 1px solid #f0f0f0;
}

.input-area textarea {
    border-radius: 12px !important;
    border: 1px solid #e5e5e5 !important;
    padding: 14px 18px !important;
    font-size: 14px !important;
    background: #fafafa !important;
    transition: all 0.15s ease !important;
    min-height: 48px !important;
    resize: none !important;
    color: #1a1a1a !important;
}

.input-area textarea:focus {
    border-color: #6366f1 !important;
    background: #ffffff !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.08) !important;
}

.input-area textarea::placeholder {
    color: #b0b0b0 !important;
}

/* 发送按钮 - Manus 风格圆形 */
.send-btn {
    background: #1a1a1a !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    min-height: 48px !important;
    min-width: 48px !important;
    transition: all 0.15s ease !important;
    box-shadow: none !important;
}

.send-btn:hover {
    background: #333333 !important;
}

/* 停止按钮 */
.stop-btn {
    background: #ffffff !important;
    color: #dc2626 !important;
    border: 1px solid #fecaca !important;
    border-radius: 12px !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    min-height: 48px !important;
    transition: all 0.15s ease !important;
}

.stop-btn:hover {
    background: #fef2f2 !important;
}

/* ===== 空白状态提示 - Manus 风格 ===== */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 80px 40px;
    color: #b0b0b0;
}

.empty-state-icon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    background: #f5f5f5;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    margin-bottom: 16px;
}

.empty-state-title {
    font-size: 16px;
    font-weight: 600;
    color: #1a1a1a;
    margin-bottom: 8px;
}

.empty-state-desc {
    font-size: 14px;
    color: #8b8b8b;
    text-align: center;
    line-height: 1.5;
}

.empty-state-examples {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 20px;
    justify-content: center;
}

.example-chip {
    background: #f5f5f5;
    border: 1px solid #e5e5e5;
    border-radius: 20px;
    padding: 8px 16px;
    font-size: 13px;
    color: #4a4a4a;
    cursor: pointer;
    transition: all 0.15s ease;
}

.example-chip:hover {
    background: #eeeeee;
    border-color: #d0d0d0;
}

/* ===== 进度指示器 ===== */
.thinking-indicator {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    color: #6366f1;
    font-size: 14px;
    font-weight: 500;
}

.thinking-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #6366f1;
    animation: thinking-pulse 1.4s infinite ease-in-out;
}

.thinking-dot:nth-child(2) { animation-delay: 0.2s; }
.thinking-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes thinking-pulse {
    0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
    40% { transform: scale(1); opacity: 1; }
}

/* ===== 代码块 ===== */
.chatbot pre {
    background: #1e1e2e !important;
    border-radius: 8px !important;
    padding: 14px !important;
    overflow-x: auto;
    margin: 8px 0 !important;
}

.chatbot code {
    font-family: 'SF Mono', 'JetBrains Mono', 'Fira Code', 'Consolas', monospace !important;
    font-size: 13px !important;
}

.chatbot p code {
    background: #f5f5f5 !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
    font-size: 13px !important;
    color: #e11d48 !important;
}

/* ===== 滚动条 - 极简 ===== */
::-webkit-scrollbar {
    width: 4px;
}

::-webkit-scrollbar-track {
    background: transparent;
}

::-webkit-scrollbar-thumb {
    background: #d0d0d0;
    border-radius: 2px;
}

::-webkit-scrollbar-thumb:hover {
    background: #b0b0b0;
}

/* ===== 任务完成标记 ===== */
.task-complete {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #f0fdf4;
    color: #16a34a;
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 13px;
    font-weight: 500;
    margin-top: 12px;
    border: 1px solid #dcfce7;
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
    .top-nav { padding: 10px 16px; }
    .chatbot .message-wrap { padding: 8px 16px !important; }
    .input-area { padding: 12px 16px 16px 16px; }
}
"""

# --- Agent Initialization for UI Server ---
ui_agent_instance: Optional[Manus] = None
ui_agent_initialized = False
ui_agent_lock = asyncio.Lock()


async def initialize_ui_agent():
    """Initializes the Manus agent instance specifically for the UI server."""
    global ui_agent_instance, ui_agent_initialized
    if not ui_agent_initialized:
        logger.info("Initializing Manus agent for UI server...")
        try:
            ui_agent_instance = Manus()
            ui_agent_instance.state = AgentState.IDLE
            ui_agent_initialized = True
            logger.info("Manus agent initialized for UI server.")
        except Exception as e:
            logger.error(f"UI Server: Failed to initialize Manus agent: {e}", exc_info=True)
            print(f"\nFATAL: Failed to initialize Manus agent for UI server: {e}\n")
            exit(1)

    if not ui_agent_instance:
        print("\nFATAL: UI Agent instance is None after initialization attempt.\n")
        exit(1)
    return ui_agent_instance


# --- File Persistence Helper Functions ---
def sanitize_filename(name: str) -> str:
    name = re.sub(r'[^\w\s-]', '', name).strip()
    name = re.sub(r'[\s-]+', '_', name)
    if not name:
        name = "untitled_chat"
    return name


def save_session_file(session_id: str, messages: List[AgentMessage]):
    try:
        HISTORY_DIR.mkdir(parents=True, exist_ok=True)
        filename = sanitize_filename(session_id) + ".json"
        filepath = HISTORY_DIR / filename
        messages_as_dicts = [msg.model_dump(mode='json') for msg in messages]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(messages_as_dicts, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved session '{session_id}' to {filepath}")
    except Exception as e:
        logger.error(f"Error saving session '{session_id}' to file: {e}", exc_info=True)
        gr.Warning(f"Failed to save session '{session_id}': {e}")


def load_session_data() -> Dict[str, List[AgentMessage]]:
    sessions = {}
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    try:
        def sort_key(p: Path):
            name = p.stem
            if name.startswith("Chat_") and len(name.split("_")) > 1 and name.split("_")[1].isdigit():
                try:
                    return (0, int(name.split("_")[1]))
                except ValueError:
                    return (1, name)
            return (1, name)

        session_files = sorted(HISTORY_DIR.glob("*.json"), key=sort_key)
        for filepath in session_files:
            session_id_from_filename = filepath.stem
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    messages_data_str = f.read()
                    if not messages_data_str.strip():
                        messages = []
                    else:
                        messages_data = json.loads(messages_data_str)
                        messages = [AgentMessage.model_validate(msg_data) 
                                    for msg_data in messages_data]
                display_name = session_id_from_filename.replace("_", " ")
                sessions[display_name] = messages
            except Exception as e:
                logger.error(f"Error loading session file {filepath}: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Error scanning session directory: {e}", exc_info=True)
    return sessions


def delete_session_file(session_id: str):
    filename = sanitize_filename(session_id) + ".json"
    filepath = HISTORY_DIR / filename
    try:
        if filepath.exists():
            filepath.unlink()
            logger.info(f"Deleted session file: {filepath}")
    except Exception as e:
        logger.error(f"Error deleting session file {filepath}: {e}", exc_info=True)


def rename_session_file(old_name: str, new_name: str):
    old_filename = sanitize_filename(old_name) + ".json"
    new_filename = sanitize_filename(new_name) + ".json"
    old_filepath = HISTORY_DIR / old_filename
    new_filepath = HISTORY_DIR / new_filename
    try:
        if old_filepath.exists():
            old_filepath.rename(new_filepath)
            logger.info(f"Renamed session file: {old_filepath} -> {new_filepath}")
    except Exception as e:
        logger.error(f"Error renaming session file: {e}", exc_info=True)


# --- Format History for Chatbot ---
def format_history_for_chatbot(messages: List[AgentMessage]) -> list:
    """Format AgentMessage list into Gradio chatbot format [[user, bot], ...]"""
    chat_pairs = []
    current_user_msg = None
    bot_parts = []

    for msg in messages:
        role = msg.role
        content = msg.content or ""

        if role == "user":
            if current_user_msg is not None:
                bot_response = "\n\n".join(bot_parts) if bot_parts else None
                chat_pairs.append([current_user_msg, bot_response])
                bot_parts = []
            current_user_msg = content
        elif role == "assistant":
            if content:
                bot_parts.append(content)
        elif role == "tool":
            tool_name = getattr(msg, 'name', 'tool')
            if content:
                short_content = content[:200] + "..." if len(content) > 200 else content
                bot_parts.append(f"`{tool_name}` 执行完成")

    if current_user_msg is not None:
        bot_response = "\n\n".join(bot_parts) if bot_parts else None
        chat_pairs.append([current_user_msg, bot_response])

    return chat_pairs


# --- Session Management UI Functions ---
def start_new_chat_session_ui(session_data: dict):
    existing_nums = []
    for key in session_data.keys():
        if key.startswith("Chat ") and key.split(" ")[-1].isdigit():
            existing_nums.append(int(key.split(" ")[-1]))
    next_num = max(existing_nums, default=0) + 1
    new_session_id = f"Chat {next_num}"
    session_data[new_session_id] = []
    save_session_file(new_session_id, [])
    updated_choices = list(session_data.keys())
    updated_choices.sort(
        key=lambda x: int(x.split(" ")[1]) if x.startswith("Chat ") and len(x.split(" ")) > 1 and x.split(" ")[1].isdigit() else float('inf')
    )
    logger.info(f"Created new session: {new_session_id}")
    return new_session_id, session_data, [], gr.Radio(choices=updated_choices, value=new_session_id)


def load_chat_session_ui(selected_session_id: str, session_data: dict):
    if not selected_session_id or selected_session_id not in session_data:
        return [], selected_session_id, gr.Radio()
    messages = session_data[selected_session_id]
    chat_history = format_history_for_chatbot(messages)
    return chat_history, selected_session_id, gr.Radio()


def delete_chat_session_ui(session_id: str, session_data: dict):
    if session_id in session_data:
        delete_session_file(session_id)
        del session_data[session_id]
        logger.info(f"Deleted session: {session_id}")
    updated_choices = list(session_data.keys())
    updated_choices.sort(
        key=lambda x: int(x.split(" ")[1]) if x.startswith("Chat ") and len(x.split(" ")) > 1 and x.split(" ")[1].isdigit() else float('inf')
    )
    if updated_choices:
        new_active = updated_choices[-1]
        new_history = format_history_for_chatbot(session_data.get(new_active, []))
    else:
        new_active = "Chat 1"
        session_data[new_active] = []
        save_session_file(new_active, [])
        updated_choices = [new_active]
        new_history = []
    return new_active, session_data, gr.Radio(choices=updated_choices, value=new_active), new_history


def rename_chat_session_ui(session_id: str, new_name: str, session_data: dict):
    if not session_id or session_id not in session_data:
        gr.Warning(f"会话 '{session_id}' 不存在！")
        return session_id, session_data, gr.Radio(choices=list(session_data.keys()), value=session_id), gr.Textbox(value="")
    if not new_name or not new_name.strip():
        gr.Warning("新名称不能为空！")
        return session_id, session_data, gr.Radio(choices=list(session_data.keys()), value=session_id), gr.Textbox(value="")
    new_name = new_name.strip()
    if new_name == session_id:
        return session_id, session_data, gr.Radio(choices=list(session_data.keys()), value=session_id), gr.Textbox(value="")
    if new_name in session_data:
        gr.Warning(f"名称 '{new_name}' 已存在！")
        return session_id, session_data, gr.Radio(choices=list(session_data.keys()), value=session_id), gr.Textbox(value="")

    rename_session_file(session_id, new_name)
    session_data[new_name] = session_data.pop(session_id)
    updated_choices = list(session_data.keys())
    updated_choices.sort(
        key=lambda x: int(x.split(" ")[1]) if x.startswith("Chat ") and len(x.split(" ")) > 1 and x.split(" ")[1].isdigit() else float('inf')
    )
    logger.info(f"Renamed session '{session_id}' to '{new_name}'")
    return new_name, session_data, gr.Radio(choices=updated_choices, value=new_name), gr.Textbox(value="")


# --- Main Chat Function ---
async def run_chat_ui(user_message: str, chat_history: list, active_session_id: str, session_data: dict):
    if not user_message or not user_message.strip():
        yield chat_history, session_data
        return

    user_message = user_message.strip()
    chat_history = chat_history or []
    chat_history.append([user_message, None])
    yield chat_history, session_data

    agent = ui_agent_instance
    if not agent:
        chat_history[-1][1] = "**错误：** Agent 未初始化，请重启服务。"
        yield chat_history, session_data
        return

    try:
        async with ui_agent_lock:
            # Reset agent state
            if agent.memory:
                if active_session_id in session_data and session_data[active_session_id]:
                    agent.memory.messages = session_data[active_session_id].copy()
                else:
                    agent.memory.messages = []
            agent.state = AgentState.IDLE
            agent.current_step = 0

            # Show thinking indicator
            chat_history[-1][1] = "正在思考中..."
            yield chat_history, session_data

            # Run the agent
            result = await agent.run(user_message)

            # Format the full conversation
            if agent.memory:
                session_data[active_session_id] = agent.memory.messages.copy()
                save_session_file(active_session_id, session_data[active_session_id])

            chat_history_formatted = format_history_for_chatbot(session_data.get(active_session_id, []))

            # Add completion marker
            if chat_history_formatted and chat_history_formatted[-1][1]:
                chat_history_formatted[-1][1] += "\n\n---\n任务完成"

            yield chat_history_formatted, session_data

    except Exception as e:
        logger.error(f"UI: Error during agent run: {e}", exc_info=True)
        error_msg = f"**发生错误：** {str(e)}"
        if chat_history:
            chat_history[-1][1] = error_msg
        if agent:
            agent.state = AgentState.ERROR
        yield chat_history, session_data
    finally:
        if agent and agent.memory:
            if active_session_id in session_data:
                session_data[active_session_id] = agent.memory.messages.copy()
                save_session_file(active_session_id, session_data[active_session_id])
        yield chat_history, session_data


# --- Build Gradio UI ---
initial_session_data = load_session_data()
initial_session_ids = list(initial_session_data.keys())
initial_session_ids.sort(
    key=lambda x: int(x.split(" ")[1]) if x.startswith("Chat ") and len(x.split(" ")) > 1 and x.split(" ")[1].isdigit() else float('inf')
)
active_session_id_on_load = initial_session_ids[-1] if initial_session_ids else "Chat 1"

with gr.Blocks(
    css=CUSTOM_CSS,
    theme=gr.themes.Base(
        primary_hue=gr.themes.colors.indigo,
        secondary_hue=gr.themes.colors.slate,
        neutral_hue=gr.themes.colors.gray,
        font=gr.themes.GoogleFont("Inter"),
        font_mono=gr.themes.GoogleFont("JetBrains Mono"),
    ),
    title="OpenManus"
) as demo:
    session_state = gr.State(initial_session_data)
    active_session_id_state = gr.State(active_session_id_on_load)

    # ===== 顶部导航栏 =====
    gr.HTML(f"""
        <div class="top-nav">
            <div class="top-nav-left">
                <div class="top-nav-logo"><span>Open</span>Manus</div>
                <div class="top-nav-model">{CURRENT_MODEL}</div>
            </div>
            <div class="top-nav-right">
                <div style="font-size:13px;color:#8b8b8b;">本地 AI Agent</div>
            </div>
        </div>
    """)

    with gr.Row(equal_height=True):
        # ===== 左侧边栏 =====
        with gr.Column(scale=1, min_width=240, elem_classes=["sidebar-wrapper"]):
            # 新建任务按钮
            new_chat_btn = gr.Button(
                "＋  新建任务",
                elem_classes=["new-task-btn"],
                size="sm"
            )

            # 任务列表标题
            gr.HTML('<div class="sidebar-header"><div class="sidebar-title">所有任务</div></div>')

            # 会话列表
            history_radio = gr.Radio(
                label="",
                choices=initial_session_ids,
                value=active_session_id_on_load,
                type="value",
                elem_classes=["session-list"],
                show_label=False
            )

            # 会话管理
            gr.HTML('<div class="manage-section"><div class="manage-label">管理</div></div>')
            rename_textbox = gr.Textbox(
                placeholder="输入新名称",
                show_label=False,
                container=False,
                scale=1
            )
            with gr.Row():
                rename_btn = gr.Button("重命名", scale=1, elem_classes=["manage-btn"], size="sm")
                delete_btn = gr.Button("删除", scale=1, elem_classes=["manage-btn", "delete-btn"], size="sm")

        # ===== 右侧主区域 =====
        with gr.Column(scale=4, elem_classes=["main-area"]):
            initial_chatbot_history = format_history_for_chatbot(
                initial_session_data.get(active_session_id_on_load, [])
            )
            chatbot = gr.Chatbot(
                value=initial_chatbot_history,
                render_markdown=True,
                height=580,
                show_label=False,
                bubble_full_width=False,
                elem_classes=["chat-area"],
                placeholder="""<div class="empty-state">
                    <div class="empty-state-icon">✦</div>
                    <div class="empty-state-title">有什么可以帮您的？</div>
                    <div class="empty-state-desc">
                        我可以帮您搜索信息、编写代码、分析数据、撰写文档等
                    </div>
                    <div class="empty-state-examples">
                        <div class="example-chip">帮我搜索最新的 AI 新闻</div>
                        <div class="example-chip">写一个 Python 爬虫</div>
                        <div class="example-chip">分析这份数据</div>
                        <div class="example-chip">帮我写一份报告</div>
                    </div>
                </div>"""
            )

            # 底部输入区域
            with gr.Row(elem_classes=["input-area"]):
                msg_textbox = gr.Textbox(
                    placeholder="描述您的任务...",
                    scale=8,
                    container=False,
                    show_label=False,
                    lines=1,
                    max_lines=5
                )
                send_btn = gr.Button(
                    "↑",
                    scale=1,
                    variant="primary",
                    min_width=48,
                    elem_classes=["send-btn"]
                )

    # --- Define Gradio Interactions ---
    submit_event = msg_textbox.submit(
        fn=run_chat_ui,
        inputs=[msg_textbox, chatbot, active_session_id_state, session_state],
        outputs=[chatbot, session_state]
    )
    submit_event.then(lambda: gr.Textbox(value=""), outputs=[msg_textbox])

    click_event = send_btn.click(
        fn=run_chat_ui,
        inputs=[msg_textbox, chatbot, active_session_id_state, session_state],
        outputs=[chatbot, session_state]
    )
    click_event.then(lambda: gr.Textbox(value=""), outputs=[msg_textbox])

    new_chat_btn.click(
        fn=start_new_chat_session_ui,
        inputs=[session_state],
        outputs=[active_session_id_state, session_state, chatbot, history_radio]
    )

    history_radio.change(
        fn=load_chat_session_ui,
        inputs=[history_radio, session_state],
        outputs=[chatbot, active_session_id_state, history_radio]
    )

    rename_btn.click(
        fn=rename_chat_session_ui,
        inputs=[active_session_id_state, rename_textbox, session_state],
        outputs=[active_session_id_state, session_state, history_radio, rename_textbox]
    )

    delete_btn.click(
        fn=delete_chat_session_ui,
        inputs=[active_session_id_state, session_state],
        outputs=[active_session_id_state, session_state, history_radio, chatbot]
    )


# --- Function to Open Browser ---
def open_browser():
    """Opens the browser to the Gradio UI."""
    try:
        logger.info(f"Attempting to open browser at {UI_BASE_URL}")
        webbrowser.open(UI_BASE_URL)
    except Exception as e:
        logger.error(f"Failed to open browser automatically: {e}")
        print(f"\nCould not open browser automatically. Please navigate to {UI_BASE_URL}\n")


# --- Main Execution ---
if __name__ == "__main__":
    try:
        asyncio.run(initialize_ui_agent())
    except SystemExit:
        exit(1)
    except Exception as e:
        print(f"\nFATAL: Unexpected error during UI agent initialization: {e}\n")
        exit(1)

    threading.Timer(1.5, open_browser).start()

    logger.info(f"Starting OpenManus UI server on {UI_BASE_URL}")
    demo.launch(server_name=UI_HOST, server_port=UI_PORT)
