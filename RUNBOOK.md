# OpenManus 本地 AI Agent 运行手册

> **版本**：v3.0 | **更新日期**：2026 年 3 月 | **作者**：Manus AI
>
> 本手册详细说明如何在 Windows 本地搭建并运行 OpenManus AI Agent 系统，包括后端 Agent 引擎和 React 前端界面的完整部署流程。

---

## 目录

1. [系统架构概览](#1-系统架构概览)
2. [环境要求](#2-环境要求)
3. [第一步：获取项目文件](#3-第一步获取项目文件)
4. [第二步：安装后端（OpenManus-GUI）](#4-第二步安装后端openmanus-gui)
5. [第三步：配置 API Key 和模型](#5-第三步配置-api-key-和模型)
6. [第四步：安装前端（React Web UI）](#6-第四步安装前端react-web-ui)
7. [第五步：启动系统](#7-第五步启动系统)
8. [第六步：验证连接](#8-第六步验证连接)
9. [日常使用](#9-日常使用)
10. [切换模型](#10-切换模型)
11. [使用本地免费模型（可选）](#11-使用本地免费模型可选)
12. [常见问题排查](#12-常见问题排查)
13. [附录：端口和服务一览](#13-附录端口和服务一览)

---

## 1. 系统架构概览

整个系统由两个独立服务组成，通过 HTTP API 通信：

```
┌─────────────────────────────────────────────────────────┐
│                    您的浏览器                              │
│              http://localhost:3000                        │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │           React 前端界面 (web-ui)                    │  │
│  │  · 任务列表 · 对话界面 · 模型选择 · 状态监控         │  │
│  │  · Vite 代理: /api → localhost:8002                  │  │
│  └──────────────────────┬─────────────────────────────┘  │
│                         │ HTTP API (通过 Vite 代理)        │
│                         ▼                                 │
│  ┌────────────────────────────────────────────────────┐  │
│  │      OpenManus-GUI 后端 (api_server.py)             │  │
│  │            http://localhost:8002                     │  │
│  │  · Agent 引擎 · 工具调用 · 浏览器自动化 · 代码执行  │  │
│  └──────────────────────┬─────────────────────────────┘  │
│                         │                                 │
│                         ▼                                 │
│              OpenAI API / Ollama 本地模型                  │
└─────────────────────────────────────────────────────────┘
```

| 服务 | 端口 | 作用 | 技术栈 |
|---|---|---|---|
| **React 前端** | 3000 | 用户界面（对话、任务管理、模型选择） | React 19 + TailwindCSS 4 + shadcn/ui |
| **OpenManus-GUI 后端** | 8002 | Agent 引擎（执行任务、调用工具） | Python + FastAPI + uvicorn |

前端通过 Vite 代理将 `/api/*` 请求转发到 `http://localhost:8002`，避免了浏览器 CORS 跨域限制。两个服务完全独立，前端只是"展示层"，不影响 Agent 的任何自动化能力。

---

## 2. 环境要求

在开始之前，请确保您的电脑已安装以下软件：

| 软件 | 最低版本 | 用途 | 下载地址 |
|---|---|---|---|
| **Python** | 3.10+ | 运行后端 Agent | [python.org/downloads](https://www.python.org/downloads/) |
| **Node.js** | 18+ | 运行前端界面 | [nodejs.org](https://nodejs.org/) |
| **Git** | 任意 | 获取项目代码 | [git-scm.com](https://git-scm.com/) |
| **pnpm** | 8+ | 前端包管理器 | 安装 Node.js 后运行 `npm install -g pnpm` |

> **重要提示**：安装 Python 时，**务必勾选 "Add Python to PATH"**。安装 Node.js 时选择 LTS 版本即可。

---

## 3. 第一步：获取项目文件

打开 PowerShell 或命令提示符，执行以下命令：

```powershell
cd E:\
git clone https://github.com/liudada118/openmanus.git openmanus
cd E:\openmanus
```

如果您已经有项目文件，只需拉取最新版本：

```powershell
cd E:\openmanus
git pull origin main
```

也可以从 GitHub 页面直接下载 ZIP：打开 [github.com/liudada118/openmanus](https://github.com/liudada118/openmanus) → 点击绿色 **Code** 按钮 → **Download ZIP** → 解压到 `E:\openmanus`。

克隆完成后，目录结构如下：

```
E:\openmanus\
├── web-ui\                      ← React 前端界面源码
│   ├── client\src\              ← 前端组件和页面
│   ├── vite.config.ts           ← Vite 配置（含代理设置）
│   ├── package.json             ← 前端依赖配置
│   └── ...
├── fix_cors.py                  ← 后端 CORS 补丁（备用方案）
├── check_deps.py                ← 依赖检查工具
├── switch_model.py              ← 模型切换工具
├── 启动全部.bat                  ← 一键启动脚本
├── 停止全部.bat                  ← 一键停止脚本
├── RUNBOOK.md                   ← 本文档
├── 中文使用说明.md
└── ARCHITECTURE.md
```

---

## 4. 第二步：安装后端（OpenManus-GUI）

### 4.1 克隆 OpenManus-GUI

```powershell
cd E:\openmanus
git clone https://github.com/Hank-Chromela/OpenManus-GUI.git
```

### 4.2 安装 Python 依赖

```powershell
cd E:\openmanus\OpenManus-GUI
pip install -r requirements.txt
```

> **提示**：不需要创建虚拟环境，直接使用系统 Python 安装即可。如果安装速度慢，可以使用国内镜像：
> ```powershell
> pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
> ```

### 4.3 安装浏览器自动化工具（可选）

```powershell
playwright install chromium
```

### 4.4 使用依赖检查工具

项目提供了自动检查工具，可以一键检测所有依赖是否安装正确：

```powershell
cd E:\openmanus
python check_deps.py
```

---

## 5. 第三步：配置 API Key 和模型

用文本编辑器（记事本即可）打开 `E:\openmanus\OpenManus-GUI\config\config.toml`，填入您的 API Key：

```toml
[llm]
model = "gpt-4.1-mini"
base_url = "https://api.openai.com/v1"
api_key = "sk-xxxxxxxxxxxxxxxxxxxxxxxx"    # ← 替换为您的 OpenAI API Key
max_tokens = 4096
temperature = 0.0
```

### 获取 API Key 的步骤

1. 用您的 GPT Plus 账号登录 [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. 点击 **"Create new secret key"**
3. **立即复制**生成的 Key（以 `sk-` 开头），之后无法再次查看
4. 粘贴到上面的 `api_key` 字段

> **费用提示**：新账号有 $5 免费额度，用 GPT-4.1-mini 大约可以免费执行 250 次任务。

---

## 6. 第四步：安装前端（React Web UI）

打开一个**新的** PowerShell 窗口，执行以下命令：

```powershell
# 1. 安装 pnpm（如果尚未安装）
npm install -g pnpm

# 2. 进入前端目录
cd E:\openmanus\web-ui

# 3. 安装前端依赖（大约 1~3 分钟）
pnpm install
```

看到 `Done` 或类似提示说明安装成功。如果网络较慢，可以先设置国内镜像：

```powershell
pnpm config set registry https://registry.npmmirror.com
```

---

## 7. 第五步：启动系统

### 方式 A：一键启动（推荐）

双击 `E:\openmanus\启动全部.bat` 即可自动启动后端和前端，并打开浏览器。

脚本会自动：
1. 检测项目安装目录
2. 启动后端 API 服务（端口 8002）
3. 启动前端开发服务器（端口 3000）
4. 打开浏览器访问 `http://localhost:3000`

### 方式 B：手动启动

**需要同时打开两个终端窗口**，分别启动后端和前端。顺序很重要：**先启动后端，再启动前端**。

**终端 1：启动后端 API 服务**

```powershell
cd E:\openmanus\OpenManus-GUI
python api_server.py
```

看到以下输出说明后端启动成功：

```
INFO:     Uvicorn running on http://0.0.0.0:8002
INFO:     Application startup complete.
```

> **注意**：这个终端窗口不要关闭，后端需要持续运行。

**终端 2：启动前端界面**

打开**另一个** PowerShell 窗口：

```powershell
cd E:\openmanus\web-ui
pnpm dev
```

看到以下输出说明前端启动成功：

```
  VITE v7.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: http://192.168.x.x:3000/
```

### 打开浏览器

在浏览器地址栏输入 **http://localhost:3000** 并回车，即可看到 Manus 风格的 AI Agent 界面。

---

## 8. 第六步：验证连接

界面打开后，请检查以下几点确认系统正常工作：

| 检查项 | 正常状态 | 异常时怎么办 |
|---|---|---|
| 右上角连接状态 | 显示绿色 **"已连接"** | 确认后端终端窗口是否正常运行 |
| 右上角齿轮图标 | 点击可打开连接设置 | 检查后端地址和端口是否正确（默认 localhost:8002） |
| 左上角模型名称 | 显示 **"GPT-4.1 Mini"** 或您配置的模型 | 点击可切换模型 |
| 输入框 | 可以正常输入文字 | 刷新页面重试 |

**快速测试**：在输入框输入"你好，请介绍一下你自己"，按 Enter 发送。如果 AI 正常回复，说明整个系统已成功连接。

---

## 9. 日常使用

每次使用时，只需要两步：

### 快速启动

**方式 1**：双击 `启动全部.bat`（推荐）

**方式 2**：手动启动

```powershell
# 终端 1（后端）
cd E:\openmanus\OpenManus-GUI && python api_server.py

# 终端 2（前端）
cd E:\openmanus\web-ui && pnpm dev
```

然后打开浏览器访问 `http://localhost:3000` 即可。

### 停止服务

双击 `停止全部.bat`，或手动在各终端窗口按 `Ctrl+C`。

---

## 10. 切换模型

### 方法 1：通过前端界面切换

点击顶部导航栏的模型名称（如"GPT-4.1 Mini"），在下拉菜单中选择想要的模型。模型分为两组：

| 分组 | 模型 | 单次任务费用 |
|---|---|---|
| **云端模型** | GPT-4.1 Mini | ¥0.14 |
| | GPT-4.1 | ¥0.72 |
| | GPT-5 Mini | ¥0.25 |
| | GPT-5.2 | ¥0.86 |
| **本地模型** | Qwen 2.5 7B | 免费 |
| | Qwen 2.5 14B | 免费 |
| | DeepSeek R1 8B | 免费 |
| | Llama 3.1 8B | 免费 |

> **注意**：前端选择模型后，后端的 `config.toml` 也需要对应修改才能真正生效。建议使用下面的命令行方式切换。

### 方法 2：通过命令行切换（推荐）

```powershell
cd E:\openmanus
python switch_model.py
```

按照提示选择模型编号即可。切换后需要**重启后端服务**才能生效（关闭后端终端窗口，重新启动）。

---

## 11. 使用本地免费模型（可选）

您的 RTX 5070（12GB 显存）可以运行本地模型，实现完全免费使用。

### 安装 Ollama

1. 从 [ollama.com/download](https://ollama.com/download) 下载并安装 Ollama
2. 安装完成后，打开终端下载模型：

```powershell
# 推荐：Qwen 2.5 14B（效果较好，12GB 显存刚好能跑）
ollama pull qwen2.5:14b

# 或者更轻量的 7B 模型（速度更快）
ollama pull qwen2.5:7b
```

3. 运行 `switch_model.py` 切换到对应的 Ollama 模型
4. 重启后端服务

> **提示**：本地模型运行时会占满显存，如果需要玩游戏或做其他 GPU 任务，请切换回云端模型。

---

## 12. 常见问题排查

### 右上角显示"未连接"

**原因**：前端无法连接到后端 API 服务。

**排查步骤**：

1. 确认后端终端窗口是否显示 `Uvicorn running on http://0.0.0.0:8002`
2. 在浏览器中直接访问 `http://localhost:8002/v1/models`，如果返回 JSON 数据说明后端正常
3. 点击右上角齿轮图标，检查连接设置中的地址和端口是否正确
4. 如果后端正常但前端仍显示未连接，运行 CORS 补丁：`python fix_cors.py`

### CORS 跨域错误

**原因**：浏览器阻止了前端直接请求后端 API。

**解决方案**（任选其一）：

1. **方案 A（已内置）**：前端已通过 Vite 代理自动解决，开发环境下 `/api/*` 请求会被代理到 `localhost:8002`
2. **方案 B（备用）**：运行 `python fix_cors.py`，自动给后端添加 CORS 中间件

### 发送消息后报错

| 错误信息 | 原因 | 解决方法 |
|---|---|---|
| API 请求失败 (401) | API Key 无效 | 检查 `config.toml` 中的 `api_key` |
| API 请求失败 (429) | 请求频率过高或余额不足 | 等待一分钟后重试，或充值 API 余额 |
| API 请求失败 (500) | 后端内部错误 | 查看后端终端窗口的错误日志 |
| 网络错误 | 后端未启动 | 确认后端终端窗口正在运行 |

### `pnpm install` 失败

1. 检查 Node.js 版本：`node -v`（需要 18+）
2. 设置国内镜像：`pnpm config set registry https://registry.npmmirror.com`
3. 清除缓存重试：`pnpm store prune && pnpm install`

### PowerShell 脚本无法运行

以管理员身份打开 PowerShell，执行：

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

输入 `Y` 回车确认。

### 端口被占用

```powershell
# 查看占用端口的进程
netstat -ano | findstr :8002    # 后端端口
netstat -ano | findstr :3000    # 前端端口

# 根据 PID 结束进程
taskkill /PID <进程ID> /F
```

### 前端页面空白

```powershell
cd E:\openmanus\web-ui
rmdir /s /q node_modules
pnpm install
pnpm dev
```

---

## 13. 附录：端口和服务一览

### 服务端口

| 服务 | 默认端口 | 启动命令 | 停止方式 |
|---|---|---|---|
| OpenManus-GUI 后端 | 8002 | `python api_server.py` | 终端按 `Ctrl+C` |
| React 前端 | 3000 | `pnpm dev` | 终端按 `Ctrl+C` |
| Ollama（可选） | 11434 | `ollama serve` | 终端按 `Ctrl+C` |

### API 端点参考

| 端点 | 方法 | 说明 |
|---|---|---|
| `http://localhost:8002/v1/chat/completions` | POST | 发送消息给 Agent（OpenAI 兼容格式，支持流式） |
| `http://localhost:8002/v1/models` | GET | 获取可用模型列表 |
| `http://localhost:3000` | — | 前端界面入口 |
| `http://localhost:3000/api/*` | — | Vite 代理（开发环境自动转发到后端 8002） |

### 文件路径速查

| 文件 | 路径 | 用途 |
|---|---|---|
| 后端配置 | `E:\openmanus\OpenManus-GUI\config\config.toml` | API Key、模型配置 |
| 前端源码 | `E:\openmanus\web-ui\client\src\` | React 组件和页面 |
| Vite 代理配置 | `E:\openmanus\web-ui\vite.config.ts` | 前端代理设置（/api → localhost:8002） |
| API 连接配置 | `E:\openmanus\web-ui\client\src\lib\api.ts` | 后端 API 地址（可在前端设置面板修改） |
| 模型切换工具 | `E:\openmanus\switch_model.py` | 命令行模型切换 |
| CORS 补丁 | `E:\openmanus\fix_cors.py` | 自动给后端添加 CORS 支持 |
| 依赖检查 | `E:\openmanus\check_deps.py` | 自动检测所有依赖是否安装 |
| 一键启动 | `E:\openmanus\启动全部.bat` | 一键启动前后端 |
| 一键停止 | `E:\openmanus\停止全部.bat` | 一键停止所有服务 |

### 工具脚本说明

| 脚本 | 用途 | 使用方法 |
|---|---|---|
| `check_deps.py` | 检查 Python、Node.js、pnpm 和所有依赖是否安装 | `python check_deps.py` |
| `fix_cors.py` | 自动给后端 api_server.py 添加 CORS 中间件 | `python fix_cors.py` |
| `switch_model.py` | 交互式切换 LLM 模型（支持 8 种预设） | `python switch_model.py` |

---

> **提示**：如果您在使用过程中遇到本手册未覆盖的问题，可以在 [GitHub Issues](https://github.com/liudada118/openmanus/issues) 中提出。
