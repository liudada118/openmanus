> **版本更新 (2026-03-02):** 已切换到 OpenManus-GUI，提供带对话历史的 Gradio Web UI，体验更佳！

# OpenManus-GUI 运行手册

本手册将指导您从零开始，在 `E:\OpenManus` 目录下安装并运行带有 Web 界面的 AI Agent 系统。

---

### 目录

1.  [**第一步：准备工作**](#第一步准备工作)
    -   [获取项目文件](#获取项目文件)
    -   [获取 OpenAI API Key](#获取-openai-api-key)
2.  [**第二步：一键安装**](#第二步一键安装)
3.  [**第三步：启动 Web UI**](#第三步启动-web-ui)
4.  [**第四步：切换模型**](#第四步切换模型)
5.  [**第五步（可选）：使用本地免费模型**](#第五步可选使用本地免费模型)
6.  [**常见问题 (FAQ)**](#常见问题-faq)

---

## 第一步：准备工作

### 获取项目文件

您有两种方式获取项目文件到 `E:\OpenManus` 目录：

**方式 A (推荐): 使用 Git**

如果您电脑上有 Git，打开终端（PowerShell 或 CMD），执行：

```bash
# 如果 E 盘还没有 OpenManus 目录
cd E:\
git clone https://github.com/liudada118/openmanus.git OpenManus

# 如果已经有，就更新
cd E:\OpenManus
git pull
```

**方式 B: 下载 ZIP 包**

1.  打开仓库地址：[https://github.com/liudada118/openmanus](https://github.com/liudada118/openmanus)
2.  点击绿色的 **Code** 按钮 → **Download ZIP**。
3.  将下载的 `openmanus-main.zip` 解压到 `E:\`，并确保文件夹名为 `OpenManus`。

### 获取 OpenAI API Key

Agent 需要调用大模型 API，您需要一个 OpenAI API Key。

1.  用您的 GPT Plus 账号登录 [platform.openai.com/api-keys](https://platform.openai.com/api-keys)。
2.  点击 **Create new secret key**。
3.  **立即复制**生成的 Key（格式为 `sk-xxxxxxxx`），因为之后无法再次查看。

> **注意**: 新账号有 $5 免费额度，用 GPT-4.1-mini 模型足够免费使用很长时间。

---

## 第二步：一键安装

1.  进入 `E:\OpenManus` 目录。
2.  找到 `install_webui_windows.ps1` 文件。
3.  **右键点击** → **使用 PowerShell 运行**。

脚本会自动完成所有安装步骤，包括：

-   克隆最新的 OpenManus-GUI 项目到 `E:\OpenManus\OpenManus-GUI`
-   创建独立的 Python 环境
-   安装所有依赖库（包括 Gradio）
-   安装浏览器自动化工具
-   提示您输入 API Key 和选择默认模型
-   在 `E:\OpenManus\OpenManus-GUI` 目录下生成启动脚本

---

## 第三步：启动 Web UI

1.  进入 `E:\OpenManus\OpenManus-GUI` 目录。
2.  双击 `启动WebUI.bat`。

脚本会自动启动服务，并**在浏览器中打开 `http://localhost:7860`**。

您会看到一个类似下图的界面，左侧是会话历史，右侧是对话框，可以开始使用了！

![Gradio UI](https://raw.githubusercontent.com/Hank-Chromela/OpenManus-GUI/main/assets/ui.png)

---

## 第四步：切换模型

如果您想在 GPT-5.2（贵但强）和 GPT-4.1-mini（便宜）之间切换，或者使用本地模型：

1.  进入 `E:\OpenManus\OpenManus-GUI` 目录。
2.  双击 `切换模型.bat`。
3.  根据提示输入数字，即可一键切换。

> **注意**: 切换模型后，需要**关闭并重新运行** `启动WebUI.bat` 才能生效。

---

## 第五步（可选）：使用本地免费模型

您的 RTX 5070 显卡可以完全免费在本地运行 Agent。

1.  **安装 Ollama**: 从 [ollama.com/download](https://ollama.com/download) 下载并安装 Ollama。
2.  **下载模型**: 打开终端，运行命令下载一个模型，例如：
    ```bash
    ollama pull qwen2.5:14b
    ```
3.  **切换模型**: 运行 `切换模型.bat`，选择对应的 Ollama 本地模型。
4.  **重启 Agent**: 重新运行 `启动WebUI.bat`。

---

## 常见问题 (FAQ)

-   **PowerShell 脚本无法运行/显示红色错误？**
    -   以管理员身份打开 PowerShell，执行 `Set-ExecutionPolicy RemoteSigned`，然后输入 `Y` 回车。这是为了允许运行本地脚本。

-   **端口 7860 被占用？**
    -   Gradio UI 默认使用 7860 端口。如果被其他程序占用，请先关闭那个程序。

-   **API Key 填错了怎么办？**
    -   直接编辑 `E:\OpenManus\OpenManus-GUI\config\config.toml` 文件，修改 `api_key` 的值即可。
