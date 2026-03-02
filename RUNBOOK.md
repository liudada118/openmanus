# OpenManus AI Agent 运行手册

这份文档将手把手带您从零开始，在 `E:\OpenManus` 目录下完整地运行您的 AI Agent 系统，包括 **Web UI 版（推荐）** 和 **终端版**。

---

## 目录

1.  [**第一步：准备工作**](#1-准备工作)
2.  [**第二步：安装 Agent (二选一)**](#2-安装-agent-二选一)
    *   [A. 安装 Web UI 版 (推荐)](#a-安装-web-ui-版-推荐)
    *   [B. 安装终端版 (经典)](#b-安装终端版-经典)
3.  [**第三步：运行 Agent**](#3-运行-agent)
    *   [运行 Web UI 版](#运行-web-ui-版)
    *   [运行终端版](#运行终端版)
4.  [**第四步：切换模型**](#4-切换模型)
5.  [**高级玩法：使用本地免费模型 (Ollama)**](#5-高级玩法使用本地免费模型-ollama)
6.  [**常见问题 (FAQ)**](#6-常见问题-faq)

---

## 1. 准备工作

在开始之前，请确保您已完成以下准备工作。

### 1.1. 获取项目文件

确保您已经将仓库的所有文件放到了 `E:\OpenManus` 目录下。

- **方式一 (推荐): 使用 Git**
  打开命令行工具 (CMD 或 PowerShell)，执行以下命令：
  ```bash
  git clone https://github.com/liudada118/openmanus.git E:\OpenManus
  ```
  如果已经克隆过，请更新到最新：
  ```bash
  cd E:\OpenManus
  git pull
  ```

- **方式二: 下载 ZIP**
  1.  访问 [https://github.com/liudada118/openmanus](https://github.com/liudada118/openmanus)
  2.  点击绿色的 **Code** 按钮 → **Download ZIP**。
  3.  将下载的 `openmanus-main.zip` 解压，并将其中的所有文件复制到 `E:\OpenManus` 目录。

### 1.2. 获取 OpenAI API Key

Agent 的“大脑”需要一个 API Key 来调用 OpenAI 的模型。**这是运行 Agent 的必需品**。

1.  **登录 OpenAI Platform**
    用您的 ChatGPT Plus 账号登录 [platform.openai.com/api-keys](https://platform.openai.com/api-keys)。

2.  **创建新的 Secret Key**
    -   点击 “**Create new secret key**”。
    -   给它起个名字，例如 `my-agent-key`。
    -   点击 “**Create secret key**”。

3.  **复制并保存 Key**
    -   点击复制按钮，将 `sk-` 开头的完整 Key 复制下来。
    -   **请务必立即将这个 Key 保存到一个安全的地方**，因为您之后将无法再次看到它。

> **费用说明**：API 是独立于 Plus 订阅计费的，但新账户有 **$5 免费额度**。使用推荐的 `GPT-4.1-mini` 模型，每次任务约 ¥0.14，免费额度足够您探索很长时间。

---

## 2. 安装 Agent (二选一)

请根据您的喜好，选择安装 **Web UI 版** 或 **终端版**。推荐使用 Web UI 版，体验更佳。

### A. 安装 Web UI 版 (推荐)

1.  **找到安装脚本**
    在 `E:\OpenManus` 目录下，找到 `install_webui_windows.ps1` 文件。

2.  **运行脚本**
    -   右键点击 `install_webui_windows.ps1`。
    -   选择 “**使用 PowerShell 运行**”。

3.  **跟随提示操作**
    -   脚本会自动检查环境、下载代码、安装依赖。
    -   当提示输入 API Key 时，将您刚才保存的 `sk-` Key 粘贴进去，然后按回车。
    -   当提示选择默认模型时，直接按回车（默认选择最经济的 `GPT-4.1-mini`）。

脚本执行完毕后，所有文件都会被安装在 `E:\OpenManus\OpenManusWeb` 目录下。

### B. 安装终端版 (经典)

1.  **找到安装脚本**
    在 `E:\OpenManus` 目录下，找到 `install_windows.ps1` 文件。

2.  **运行脚本**
    -   右键点击 `install_windows.ps1`。
    -   选择 “**使用 PowerShell 运行**”。

3.  **跟随提示操作**
    -   过程与 Web UI 版类似，按提示输入 API Key 和选择模型即可。

脚本执行完毕后，所有文件都会被安装在 `E:\OpenManus` 目录下。

---

## 3. 运行 Agent

安装完成后，您就可以启动 Agent 了。

### 运行 Web UI 版

1.  进入 `E:\OpenManus\OpenManusWeb` 目录。
2.  双击 `启动WebUI.bat` 文件。
3.  一个终端窗口会弹出并开始运行服务器。
4.  在您的浏览器中访问 [**http://localhost:8000**](http://localhost:8000)。

现在您可以看到一个类似 ChatGPT 的界面，在输入框中输入您的任务（例如：“帮我查找一下今天关于人工智能的最新新闻”），然后按发送，Agent 就会开始工作了！

### 运行终端版

1.  进入 `E:\OpenManus` 目录。
2.  双击 `启动Agent.bat` 文件。
3.  一个终端窗口会弹出，提示您输入任务。直接在窗口中输入任务目标，按回车即可。

---

## 4. 切换模型

您可以随时切换 Agent 使用的“大脑”，以平衡成本和性能。

1.  **找到切换脚本**
    -   如果您安装了 Web UI 版，脚本在 `E:\OpenManus\OpenManusWeb` 目录下。
    -   如果您安装了终端版，脚本在 `E:\OpenManus` 目录下。

2.  **运行 `切换模型.bat`**
    双击 `切换模型.bat` 文件。

3.  **选择模型**
    一个菜单会显示所有可用的模型。输入您想切换的模型的数字，然后按回车即可。

---

## 5. 高级玩法：使用本地免费模型 (Ollama)

您的 RTX 5070 显卡足以在本地运行强大的开源模型，实现完全免费、离线使用。

1.  **安装 Ollama**
    从 [ollama.com/download](https://ollama.com/download) 下载并安装 Ollama for Windows。

2.  **下载模型**
    打开命令行 (CMD)，执行以下命令下载一个推荐的模型：
    ```bash
    ollama pull qwen2.5:14b
    ```
    （下载过程会需要一些时间）

3.  **切换到 Ollama 模型**
    -   运行 `切换模型.bat`。
    -   选择列表中对应的 Ollama 模型（例如 `Qwen2.5 14B`）。

切换成功后，再次启动 Agent，它就会使用您本地的显卡进行计算，不再消耗 OpenAI API 费用。

---

## 6. 常见问题 (FAQ)

**Q: 运行 PowerShell 脚本提示“禁止运行脚本”怎么办？**

A: 这是 Windows 的安全策略。请打开一个新的 PowerShell 窗口，输入 `Set-ExecutionPolicy Bypass -Scope Process`，然后按回车。之后再重新运行安装脚本即可。

**Q: Web UI 界面打不开 (http://localhost:8000)？**

A: 请检查运行 `启动WebUI.bat` 的终端窗口中是否有报错信息。如果提示端口被占用，您可以联系我帮您修改端口号。

**Q: API Key 填错了怎么办？**

A: 没关系。直接用记事本打开配置文件 `E:\OpenManus\OpenManusWeb\config\config.toml` (Web UI 版) 或 `E:\OpenManus\config\config.toml` (终端版)，找到 `api_key = "sk-..."` 这一行，修改成正确的 Key 即可。

**Q: 我可以把这些文件放到别的盘吗？**

A: 可以，但您需要手动修改所有 `.ps1` 和 `.bat` 文件中的 `E:\OpenManus` 路径为您自己的路径。

---

祝您使用愉快！

**Manus AI**
