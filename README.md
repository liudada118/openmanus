# OpenManus 本地 AI Agent 一键部署包

欢迎使用由 Manus AI 为您定制的 OpenManus 本地部署包！

这个包可以帮您一键搭建一个功能强大、类似 Manus 的本地 AI Agent 系统。它基于开源项目 [OpenManus](https://github.com/FoundationAgents/OpenManus)，并为您集成了便捷的一键安装、模型切换和快捷启动功能。

---

## 核心功能

- **一键安装**：无需手动配置复杂环境，在 Windows、macOS 或 Linux 上运行一个脚本即可完成所有安装。
- **多模型切换**：内置模型切换工具，可以随时在以下模型中灵活切换，兼顾性能与成本：
    - **GPT-5.2** (最强模型)
    - **GPT-4.1-mini** (性价比之王)
    - **GPT-5-mini** (平衡选择)
    - **Ollama 本地模型** (完全免费，利用您的 GPU)
- **与 Manus 类似的核心能力**：
    - **网页浏览与信息提取**
    - **代码编写、执行与调试**
    - **文件操作与数据分析**
    - **长短期记忆**

## 快速开始

### 第一步：下载部署包

下载本文件夹 (`my-agent-setup`) 到您的电脑上。

### 第二步：运行一键安装脚本

根据您的操作系统，选择对应的脚本运行：

#### Windows 用户

1.  右键点击 `install_windows.ps1` 文件。
2.  选择 “**使用 PowerShell 运行**”。
3.  脚本会自动安装 Python, uv, OpenManus, 并设置好一切。

> **注意**: 如果提示“无法加载文件...因为在此系统上禁止运行脚本”，请打开一个新的 PowerShell 窗口，输入以下命令后再试：
> `Set-ExecutionPolicy Bypass -Scope Process`

#### macOS / Linux 用户

1.  打开您的终端 (Terminal)。
2.  进入本文件夹: `cd /path/to/my-agent-setup`
3.  给脚本添加执行权限: `chmod +x install_unix.sh`
4.  运行脚本: `./install_unix.sh`

安装过程中，脚本会提示您输入 **OpenAI API Key**。您可以从 [platform.openai.com/api-keys](https://platform.openai.com/api-keys) 获取。如果没有，可以直接按回车跳过，稍后手动修改配置文件。

### 第三步：启动 Agent

安装完成后，所有文件都会被放在您用户主目录下的 `OpenManus` 文件夹里 (`C:\Users\YourName\OpenManus` 或 `~/OpenManus`)。

- **Windows**: 双击 `OpenManus` 文件夹里的 `启动Agent.bat` 文件。
- **macOS / Linux**: 在终端执行 `~/OpenManus/start.sh`。

启动后，您就可以在终端里输入您的任务目标，开始与 AI Agent 交互了！

## 如何切换模型？

我们为您准备了方便的模型切换工具。

- **Windows**: 双击 `OpenManus` 文件夹里的 `切换模型.bat` 文件。
- **macOS / Linux**: 在终端执行 `cd ~/OpenManus && source .venv/bin/activate && python switch_model.py`。

您会看到一个菜单，列出了所有预设的模型，包括 OpenAI 的各种模型和本地 Ollama 模型。输入数字即可轻松切换。

### 使用本地 Ollama 模型

如果您想实现完全免费、100% 本地运行，可以选择 Ollama 模型。您的 RTX 5070 显卡足以流畅运行 14B 规模的模型。

1.  **安装 Ollama**: 从 [ollama.com/download](https://ollama.com/download) 下载并安装 Ollama。
2.  **下载模型**: 在终端执行 `ollama pull qwen2.5:14b` (推荐) 或 `ollama pull llama3.3:8b`。
3.  **切换模型**: 运行模型切换工具，选择对应的 Ollama 模型即可。

## 常见问题 (FAQ)

**Q: OpenAI API Key 在哪里获取？收费吗？**

A: 您可以用您的 ChatGPT Plus 账号登录 [platform.openai.com/api-keys](https://platform.openai.com/api-keys) 创建。API 是独立于 Plus 订阅计费的，但新注册用户有 **$5 免费额度**，使用 GPT-4.1-mini 的话，足够免费用很久了。

**Q: 为什么推荐使用 GPT-4.1-mini？**

A: 因为它在性能、价格和速度上达到了完美的平衡。对于绝大多数通用 Agent 任务，它的能力绰绰有余，而且成本极低（每次任务约 ¥0.14），是日常使用的最佳选择。

**Q: 启动时报错怎么办？**

A: 请确保您已经按照安装脚本的指引正确安装了所有依赖。如果问题仍然存在，可以尝试删除 `OpenManus` 文件夹，然后重新运行一次安装脚本。

**Q: 我可以自己添加其他模型吗？**

A: 当然可以！运行模型切换工具时，选择“自定义模型”，然后输入模型的名称、API Base URL 和 API Key 即可。

---

祝您使用愉快！

**Manus AI**
