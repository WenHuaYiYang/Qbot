# Qbot

> 一个基于 NapCat 的 QQ 聊天机器人，可接入大模型，扮演《葬送的芙莉莲》中的勇者辛美尔。

## ✨ 功能特点

- 自动响应私聊
- 支持接入大模型
- 角色扮演：温柔自恋的勇者辛美尔，回答简洁，偶尔送用户一朵“苍月草”
- 自动处理加好友请求（默认验证暗号：`3月29号`）
- WebSocket 与 NapCat 通信，稳定可靠

## 🚀 食用方法

### 1. 安装 NapCat

NapCat 是 QQ 协议的实现，负责与腾讯服务器通信。请根据你的操作系统下载并安装：

- 访问 [NapCat 官方仓库](https://github.com/NapNeko/NapCatQQ) 下载最新版。
- 解压后运行 `napcat.bat`（Windows）或 `napcat`（Linux/macOS）。
- 首次启动会弹出浏览器，扫码登录你的 QQ 小号（建议使用专用账号）。
- 登录后，请设置你的 WebSocket 服务端。

> 💡 你也可以使用 Docker 部署 NapCat，请参考官方文档。

### 2. 配置 NapCat WebSocket 连接

本项目使用 **WebSocket 客户端模式**（NapCat 作为服务端，Python 程序主动连接）。确认 NapCat 的 WebSocket 配置：

- 打开 NapCat WebUI
- 进入 **网络配置** → 确保 **WebSocket 服务端** 已启用，并设置端口

### 3. 安装 uv 并创建虚拟环境

本项目使用 [uv](https://docs.astral.sh/uv/) 进行依赖管理。确保你已安装 Python 3.11+，然后安装 uv：

```bash
# 安装 uv（推荐使用官方脚本）
curl -LsSf https://astral.sh/uv/install.sh | sh
# 或使用 pip 安装
pip install uv
```

克隆本项目并进入目录，创建虚拟环境并安装依赖：

```bash
cd Qbot https://github.com/WHEN-HUA-YIYANG/Qbot.git
uv venv  # 创建虚拟环境（默认 .venv）
source .venv/bin/activate  # Linux/macOS 激活；Windows 用 .venv\Scripts\activate
uv sync
```
### 4. 运行项目

```bash
# 确保虚拟环境已激活
python main.py
```
