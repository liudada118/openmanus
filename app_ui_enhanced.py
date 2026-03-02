# app_ui_enhanced.py - Enhanced Gradio UI with modern styling
# 替换原版 app_ui.py，提供更美观的界面体验
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
# 自定义 CSS 样式 - 现代化深色主题
# ============================================================
CUSTOM_CSS = """
/* ===== 全局样式 ===== */
.gradio-container {
    max-width: 100% !important;
    font-family: 'Inter', 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
}

/* ===== 顶部标题区域 ===== */
.header-banner {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 16px;
    padding: 20px 30px;
    margin-bottom: 16px;
    color: white;
    text-align: center;
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
}

.header-banner h1 {
    margin: 0;
    font-size: 28px;
    font-weight: 700;
    letter-spacing: -0.5px;
    color: white !important;
}

.header-banner p {
    margin: 6px 0 0 0;
    font-size: 14px;
    opacity: 0.85;
    color: white !important;
}

/* ===== 模型状态徽章 ===== */
.model-badge {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    border-radius: 20px;
    padding: 8px 16px;
    text-align: center;
    margin-bottom: 12px;
    box-shadow: 0 2px 10px rgba(245, 87, 108, 0.2);
}

.model-badge p {
    margin: 0;
    font-size: 13px;
    color: white !important;
    font-weight: 600;
}

/* ===== 左侧栏样式 ===== */
.sidebar-section {
    background: #f8f9fc;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
    border: 1px solid #e8ecf4;
}

.sidebar-section h3, .sidebar-section h2 {
    color: #4a5568 !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    margin-bottom: 10px !important;
}

/* ===== 新建对话按钮 ===== */
.new-chat-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 10px 20px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3) !important;
}

.new-chat-btn:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
}

/* ===== 会话列表 Radio 样式 ===== */
.session-radio .wrap {
    gap: 4px !important;
}

.session-radio label {
    border-radius: 8px !important;
    padding: 8px 12px !important;
    margin: 2px 0 !important;
    transition: all 0.2s ease !important;
    border: 1px solid transparent !important;
}

.session-radio label:hover {
    background: #eef2ff !important;
    border-color: #c7d2fe !important;
}

.session-radio label.selected {
    background: #eef2ff !important;
    border-color: #818cf8 !important;
    font-weight: 600 !important;
}

/* ===== 聊天区域 ===== */
.chatbot-container {
    border-radius: 16px !important;
    border: 1px solid #e8ecf4 !important;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04) !important;
}

/* 聊天气泡样式 */
.chatbot .message-wrap .message {
    border-radius: 16px !important;
    padding: 12px 16px !important;
    font-size: 14px !important;
    line-height: 1.6 !important;
}

.chatbot .message-wrap .message.user {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border-bottom-right-radius: 4px !important;
}

.chatbot .message-wrap .message.bot {
    background: #f8f9fc !important;
    color: #2d3748 !important;
    border: 1px solid #e8ecf4 !important;
    border-bottom-left-radius: 4px !important;
}

/* ===== 输入框样式 ===== */
.input-row textarea {
    border-radius: 12px !important;
    border: 2px solid #e8ecf4 !important;
    padding: 12px 16px !important;
    font-size: 14px !important;
    transition: border-color 0.3s ease !important;
    min-height: 50px !important;
}

.input-row textarea:focus {
    border-color: #818cf8 !important;
    box-shadow: 0 0 0 3px rgba(129, 140, 248, 0.1) !important;
}

/* ===== 发送按钮 ===== */
.send-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    min-height: 50px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3) !important;
}

.send-btn:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
}

/* ===== 管理按钮 ===== */
.manage-btn {
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
}

/* ===== 底部状态栏 ===== */
.footer-bar {
    text-align: center;
    padding: 12px;
    color: #a0aec0;
    font-size: 12px;
    border-top: 1px solid #e8ecf4;
    margin-top: 16px;
}

.footer-bar p {
    margin: 0;
}

/* ===== 滚动条美化 ===== */
::-webkit-scrollbar {
    width: 6px;
}

::-webkit-scrollbar-track {
    background: transparent;
}

::-webkit-scrollbar-thumb {
    background: #cbd5e0;
    border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
    background: #a0aec0;
}

/* ===== 代码块样式 ===== */
.chatbot pre {
    background: #1a1b26 !important;
    border-radius: 10px !important;
    padding: 14px !important;
    overflow-x: auto;
}

.chatbot code {
    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace !important;
    font-size: 13px !important;
}

/* ===== 响应式调整 ===== */
@media (max-width: 768px) {
    .header-banner h1 {
        font-size: 22px;
    }
    .header-banner p {
        font-size: 12px;
    }
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
                        messages = [AgentMessage.model_validate(msg_data) for msg_data in messages_data]
                    sessions[session_id_from_filename] = messages
                logger.debug(f"Loaded session '{session_id_from_filename}' from {filepath}")
            except Exception as e:
                logger.error(f"Error loading session file {filepath}: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Error reading history directory '{HISTORY_DIR}': {e}", exc_info=True)
    if not sessions:
        logger.info("No chat history found. Starting with 'Chat 1'.")
        default_session_id = "Chat 1"
        sessions[default_session_id] = []
        save_session_file(default_session_id, [])
    logger.info(f"Loaded {len(sessions)} sessions.")
    return sessions


def delete_session_file(session_id: str):
    try:
        filename = sanitize_filename(session_id) + ".json"
        filepath = HISTORY_DIR / filename
        if filepath.exists():
            filepath.unlink()
            logger.info(f"Deleted session file: {filepath}")
        else:
            logger.warning(f"Attempted to delete non-existent session file: {filepath}")
    except Exception as e:
        logger.error(f"Error deleting session file for '{session_id}': {e}", exc_info=True)
        gr.Error(f"Failed to delete session file for '{session_id}': {e}")


def rename_session_file(old_session_id: str, new_session_id: str):
    try:
        old_filename = sanitize_filename(old_session_id) + ".json"
        new_filename = sanitize_filename(new_session_id) + ".json"
        old_filepath = HISTORY_DIR / old_filename
        new_filepath = HISTORY_DIR / new_filename
        if old_filepath.exists():
            if not new_filepath.exists():
                old_filepath.rename(new_filepath)
                logger.info(f"Renamed session file from {old_filename} to {new_filename}")
            else:
                logger.error(f"Rename failed: Target file '{new_filename}' already exists.")
                gr.Error(f"Rename failed: File for '{new_session_id}' already exists.")
        else:
            logger.warning(f"Attempted to rename non-existent session file: {old_filepath}")
            gr.Warning(f"Could not find file for '{old_session_id}' to rename.")
    except Exception as e:
        logger.error(f"Error renaming session file: {e}", exc_info=True)
        gr.Error(f"Failed to rename session file: {e}")


# --- UI Helper Function ---
def format_history_for_chatbot(messages: list[AgentMessage]) -> list[list[str | None]]:
    chatbot_history = []
    user_msg_content = None
    assistant_msg_parts = []

    for msg in messages:
        if msg.role == "user":
            if assistant_msg_parts:
                if user_msg_content is not None:
                    chatbot_history.append([user_msg_content, "\n\n".join(assistant_msg_parts)])
                else:
                    chatbot_history.append([None, "\n\n".join(assistant_msg_parts)])
                assistant_msg_parts = []
            user_msg_content = msg.content
        elif msg.role == "assistant":
            thought_prefix = "💭 **思考过程：**\n" if msg.content else ""
            tool_calls_str = ""
            if msg.tool_calls:
                tool_calls_str = "\n🔧 **调用工具：**\n" + "\n".join(
                    [f"- `{tc.function.name}`(`{tc.function.arguments or '{}'}`)" for tc in msg.tool_calls]
                )
            assistant_msg_parts.append(f"{thought_prefix}{msg.content or ''}{tool_calls_str}")
        elif msg.role == "tool":
            tool_content = str(msg.content)
            is_code = "```" in tool_content
            formatted_content = tool_content if is_code else f"```\n{tool_content}\n```"
            if len(tool_content) > 500 and "..." not in tool_content[-10:]:
                formatted_content = formatted_content[:500] + "..."
            assistant_msg_parts.append(f"📋 **工具结果 (`{msg.name}`)：**\n{formatted_content}")
        elif msg.role == "system":
            assistant_msg_parts.append(f"⚙️ **系统提示：**\n{msg.content}")

    if user_msg_content is not None:
        chatbot_history.append([
            user_msg_content,
            "\n\n".join(assistant_msg_parts) if assistant_msg_parts else None
        ])
    elif assistant_msg_parts:
        chatbot_history.append([None, "\n\n".join(assistant_msg_parts)])

    return chatbot_history


# --- Gradio Session Management Functions ---
def start_new_chat_session_ui(session_data: dict):
    existing_nums = []
    for sid in session_data.keys():
        if sid.startswith("Chat ") and len(sid.split(" ")) > 1 and sid.split(" ")[1].isdigit():
            existing_nums.append(int(sid.split(" ")[1]))
    next_num = max(existing_nums, default=0) + 1
    new_session_id = f"Chat {next_num}"
    session_data[new_session_id] = []
    save_session_file(new_session_id, [])
    updated_choices = list(session_data.keys())
    updated_choices.sort(
        key=lambda x: int(x.split(" ")[1]) if x.startswith("Chat ") and len(x.split(" ")) > 1 and x.split(" ")[1].isdigit() else float('inf')
    )
    logger.info(f"Created new chat session: {new_session_id}")
    return new_session_id, session_data, [], gr.Radio(choices=updated_choices, value=new_session_id)


def load_chat_session_ui(selected_session_id: str, session_data: dict):
    if selected_session_id and selected_session_id in session_data:
        messages = session_data[selected_session_id]
        chatbot_history = format_history_for_chatbot(messages)
        logger.info(f"Loaded session: {selected_session_id} with {len(messages)} messages")
        return chatbot_history, selected_session_id, gr.Radio(value=selected_session_id)
    return [], selected_session_id, gr.Radio(value=selected_session_id)


def delete_chat_session_ui(session_id: str, session_data: dict):
    if not session_id or session_id not in session_data:
        gr.Warning(f"Session '{session_id}' not found!")
        return session_id, session_data, gr.Radio(choices=list(session_data.keys()), value=session_id), []

    delete_session_file(session_id)
    del session_data[session_id]

    if not session_data:
        session_data["Chat 1"] = []
        save_session_file("Chat 1", [])

    updated_choices = list(session_data.keys())
    updated_choices.sort(
        key=lambda x: int(x.split(" ")[1]) if x.startswith("Chat ") and len(x.split(" ")) > 1 and x.split(" ")[1].isdigit() else float('inf')
    )
    new_active = updated_choices[-1] if updated_choices else "Chat 1"
    new_history = format_history_for_chatbot(session_data.get(new_active, []))
    logger.info(f"Deleted session: {session_id}, switched to: {new_active}")
    return new_active, session_data, gr.Radio(choices=updated_choices, value=new_active), new_history


def rename_chat_session_ui(session_id: str, new_name: str, session_data: dict):
    if not session_id or session_id not in session_data:
        gr.Warning(f"Session '{session_id}' not found!")
        return session_id, session_data, gr.Radio(choices=list(session_data.keys()), value=session_id), gr.Textbox(value="")
    if not new_name or not new_name.strip():
        gr.Warning("New name cannot be empty!")
        return session_id, session_data, gr.Radio(choices=list(session_data.keys()), value=session_id), gr.Textbox(value="")
    new_name = new_name.strip()
    if new_name == session_id:
        return session_id, session_data, gr.Radio(choices=list(session_data.keys()), value=session_id), gr.Textbox(value="")
    if new_name in session_data:
        gr.Warning(f"Name '{new_name}' already exists!")
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
        chat_history[-1][1] = "❌ **错误：** Agent 未初始化，请重启服务。"
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
            chat_history[-1][1] = "🤔 **正在思考中...**"
            yield chat_history, session_data

            # Run the agent
            result = await agent.run(user_message)

            # Format the full conversation
            if agent.memory:
                session_data[active_session_id] = agent.memory.messages.copy()
                save_session_file(active_session_id, session_data[active_session_id])

            chat_history_formatted = format_history_for_chatbot(session_data.get(active_session_id, []))

            # Add success indicator
            if chat_history_formatted and chat_history_formatted[-1][1]:
                chat_history_formatted[-1][1] += "\n\n✅ **任务完成**"

            yield chat_history_formatted, session_data

    except Exception as e:
        logger.error(f"UI: Error during agent run: {e}", exc_info=True)
        error_msg = f"❌ **发生错误：** {str(e)}"
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
    theme=gr.themes.Soft(
        primary_hue=gr.themes.colors.indigo,
        secondary_hue=gr.themes.colors.purple,
        neutral_hue=gr.themes.colors.slate,
        font=gr.themes.GoogleFont("Inter"),
    ),
    title="OpenManus Agent"
) as demo:
    session_state = gr.State(initial_session_data)
    active_session_id_state = gr.State(active_session_id_on_load)

    # ===== 顶部标题栏 =====
    gr.HTML(f"""
        <div class="header-banner">
            <h1>🤖 OpenManus Agent</h1>
            <p>本地 AI 智能助手 · 支持上网搜索 · 代码编写 · 文件操作 · 数据分析</p>
        </div>
    """)

    with gr.Row():
        # ===== 左侧栏 =====
        with gr.Column(scale=1, min_width=280):
            # 模型状态
            gr.HTML(f"""
                <div class="model-badge">
                    <p>🧠 当前模型：{CURRENT_MODEL}</p>
                </div>
            """)

            # 新建对话按钮
            new_chat_btn = gr.Button(
                "✨ 新建对话",
                elem_classes=["new-chat-btn"],
                size="lg"
            )

            # 会话列表
            gr.HTML("<div class='sidebar-section'><h3>📂 对话历史</h3></div>")
            history_radio = gr.Radio(
                label="",
                choices=initial_session_ids,
                value=active_session_id_on_load,
                type="value",
                elem_classes=["session-radio"],
                show_label=False
            )

            # 会话管理
            gr.HTML("<div class='sidebar-section'><h3>⚙️ 管理会话</h3></div>")
            rename_textbox = gr.Textbox(
                placeholder="输入新名称...",
                show_label=False,
                container=False
            )
            with gr.Row():
                rename_btn = gr.Button("✏️ 重命名", scale=1, elem_classes=["manage-btn"])
                delete_btn = gr.Button("🗑️ 删除", scale=1, variant="stop", elem_classes=["manage-btn"])

        # ===== 右侧聊天区域 =====
        with gr.Column(scale=4):
            initial_chatbot_history = format_history_for_chatbot(
                initial_session_data.get(active_session_id_on_load, [])
            )
            chatbot = gr.Chatbot(
                value=initial_chatbot_history,
                render_markdown=True,
                height=620,
                show_label=False,
                bubble_full_width=False,
                elem_classes=["chatbot-container"],
                placeholder="<div style='text-align:center;color:#a0aec0;padding:40px;'>"
                           "<p style='font-size:48px;margin-bottom:16px;'>🤖</p>"
                           "<p style='font-size:18px;font-weight:600;'>有什么我可以帮您的？</p>"
                           "<p style='font-size:14px;margin-top:8px;'>试试输入：帮我写一个 Python 爬虫 / 帮我搜索最新的 AI 新闻</p>"
                           "</div>"
            )

            with gr.Row(elem_classes=["input-row"]):
                msg_textbox = gr.Textbox(
                    placeholder="输入您的任务或问题... (按 Enter 发送)",
                    scale=7,
                    container=False,
                    show_label=False,
                    lines=1,
                    max_lines=5
                )
                send_btn = gr.Button(
                    "发送 ➤",
                    scale=1,
                    variant="primary",
                    min_width=100,
                    elem_classes=["send-btn"]
                )

    # ===== 底部状态栏 =====
    gr.HTML(f"""
        <div class="footer-bar">
            <p>OpenManus Agent · 当前模型: {CURRENT_MODEL} · 对话历史自动保存</p>
        </div>
    """)

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

    logger.info(f"Starting Enhanced Gradio UI server on {UI_BASE_URL}")
    demo.launch(server_name=UI_HOST, server_port=UI_PORT)
