# 飞书共同空闲时间查询机器人

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Lark SDK](https://img.shields.io/badge/lark--oapi-%E2%89%A51.4.0-orange)](https://github.com/larksuite/oapi-sdk-python)

> 飞书机器人：在群聊中 @机器人 + @成员，即可查询多人共同空闲时间，帮助团队高效安排会议。

---

## ✨ 功能特性

- 📩 **消息触发** — 被 @ 时自动接收消息事件
- ⏳ **即时反馈** — 收到消息先添加 `OneSecond` 表情，处理完成后替换为 `DONE`
- 📅 **日历查询** — 查询消息内被 @ 成员（自动排除机器人）的日历忙碌信息
- 🧮 **智能计算** — 基于"忙碌时间并集的补集"算法，计算多人共同空闲时段
- 📊 **美观输出** — 结果以 Markdown 代码块表格形式展示
- 📖 **使用引导** — 用户进入会话或机器人进群时自动发送查询指引

## 📁 目录结构

```
Lark_FreeTime/
├── main.py                 # 长连接事件入口
├── bot/
│   ├── __init__.py         # 包标记
│   ├── config.py           # 配置加载
│   ├── feishu_client.py    # 飞书 API 封装
│   └── scheduler.py        # 共同空闲时间计算
├── requirements.txt        # Python 依赖
├── .env.example            # 环境变量模板
├── .gitignore
├── LICENSE                 # MIT 许可证
├── README.md               # 项目说明文档
├── CONTRIBUTING.md         # 贡献指南
├── CODE_OF_CONDUCT.md      # 行为准则
└── SECURITY.md             # 安全政策
```

---

## 🚀 快速开始

### 前置条件

- **Git** — 用于克隆项目仓库
- **Python 3.10+** — 项目运行环境
- **飞书开发者账号** — 用于创建自定义机器人应用

---

### 第一步：安装 Git

<details>
<summary><b>🪟 Windows</b></summary>

1. 前往 [Git 官方下载页](https://git-scm.com/downloads/win) 下载 Windows 安装包。
2. 运行安装程序，使用默认选项即可（一直点击 **Next**）。
3. 安装完成后，打开 **Git Bash** 或 **命令提示符（cmd）**，验证安装：
   ```bash
   git --version
   ```
   出现类似 `git version 2.x.x` 的输出即表示安装成功。

</details>

<details>
<summary><b>🍎 macOS</b></summary>

**方式一：使用 Homebrew（推荐）**

如果你已安装 [Homebrew](https://brew.sh/)，在终端中运行：

```bash
brew install git
```

**方式二：使用 Xcode 命令行工具**

在终端中运行以下命令，系统会提示安装命令行开发工具（含 Git）：

```bash
xcode-select --install
```

验证安装：

```bash
git --version
```

</details>

<details>
<summary><b>🐧 Linux</b></summary>

根据你的发行版选择对应命令：

**Debian / Ubuntu：**

```bash
sudo apt update && sudo apt install -y git
```

**Fedora：**

```bash
sudo dnf install -y git
```

**Arch Linux：**

```bash
sudo pacman -S git
```

**CentOS / RHEL：**

```bash
sudo yum install -y git
```

验证安装：

```bash
git --version
```

</details>

---

### 第二步：安装 Python 3.10+

<details>
<summary><b>🪟 Windows</b></summary>

1. 前往 [Python 官方下载页](https://www.python.org/downloads/) 下载最新版本安装包。
2. 运行安装程序时，**务必勾选底部的 `Add Python to PATH`**（非常重要）。
3. 点击 **Install Now** 完成安装。
4. 打开 **命令提示符（cmd）** 或 **PowerShell**，验证安装：
   ```bash
   python --version
   ```
   出现类似 `Python 3.1x.x` 的输出即表示安装成功。

> 💡 **提示**：若命令无效，请尝试使用 `python3 --version`，或检查是否已将 Python 添加到系统 PATH 环境变量中。

</details>

<details>
<summary><b>🍎 macOS</b></summary>

**方式一：使用 Homebrew（推荐）**

```bash
brew install python
```

安装完成后验证：

```bash
python3 --version
```

**方式二：使用官方安装包**

1. 前往 [Python 官方下载页](https://www.python.org/downloads/macos/) 下载最新版 macOS 安装包。
2. 运行 `.pkg` 安装程序，按照提示完成安装。
3. 验证安装：
   ```bash
   python3 --version
   ```

> 💡 **提示**：macOS 自带的 Python 版本可能较旧，建议通过 Homebrew 或官方安装包安装最新版本。

</details>

<details>
<summary><b>🐧 Linux</b></summary>

大多数 Linux 发行版已预装 Python 3，先检查版本：

```bash
python3 --version
```

如果版本低于 3.10，或未安装 Python，根据你的发行版选择安装方式：

**Debian / Ubuntu：**

```bash
sudo apt update && sudo apt install -y python3 python3-pip python3-venv
```

**Fedora：**

```bash
sudo dnf install -y python3 python3-pip
```

**Arch Linux：**

```bash
sudo pacman -S python python-pip
```

**CentOS / RHEL（需启用 EPEL 或使用源码编译）：**

```bash
sudo yum install -y python3 python3-pip
```

> 💡 **提示**：如果系统仓库中 Python 版本较旧，可考虑使用 [pyenv](https://github.com/pyenv/pyenv) 安装和管理多个 Python 版本。

</details>

---

### 第三步：克隆项目

打开终端（Windows 用户可使用 Git Bash、命令提示符或 PowerShell），运行以下命令：

```bash
git clone https://github.com/qq940500529/Lark_FreeTime.git
cd Lark_FreeTime
```

---

### 第四步：创建虚拟环境（推荐）

使用虚拟环境可以隔离项目依赖，避免与系统全局包冲突。

<details>
<summary><b>🪟 Windows</b></summary>

```bash
# cmd
python -m venv venv
venv\Scripts\activate

# PowerShell
python -m venv venv
venv\Scripts\Activate.ps1

# Git Bash
python -m venv venv
source venv/Scripts/activate
```

激活成功后，命令行前缀会出现 `(venv)` 字样。

</details>

<details>
<summary><b>🍎 macOS / 🐧 Linux</b></summary>

```bash
python3 -m venv venv
source venv/bin/activate
```

激活成功后，命令行前缀会出现 `(venv)` 字样。

</details>

---

### 第五步：安装依赖

```bash
pip install -r requirements.txt
```

---

### 第六步：配置环境变量

复制模板并编辑：

<details>
<summary><b>🪟 Windows（命令提示符）</b></summary>

```bash
copy .env.example .env
```

然后用文本编辑器（如记事本）打开 `.env` 文件进行编辑。

</details>

<details>
<summary><b>🪟 Windows（PowerShell）</b></summary>

```powershell
Copy-Item .env.example .env
```

然后用文本编辑器打开 `.env` 文件进行编辑。

</details>

<details>
<summary><b>🍎 macOS / 🐧 Linux</b></summary>

```bash
cp .env.example .env
```

使用你喜欢的编辑器打开 `.env` 文件：

```bash
nano .env    # 或者使用 vim .env
```

</details>

填写以下内容（项目已支持从 `.env` 文件自动读取）：

```env
FEISHU_APP_ID=你的应用ID
FEISHU_APP_SECRET=你的应用密钥
# 可选：若你已知机器人 open_id，可配置以更稳定地排除机器人
FEISHU_BOT_OPEN_ID=ou_xxx
```

> 📝 `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET` 可在 [飞书开放平台 - 应用凭证](https://open.feishu.cn/app) 页面获取。

---

### 第七步：运行

```bash
python main.py
```

看到日志输出即表示机器人已成功启动，正在通过长连接监听飞书事件 🎉

> 💡 **提示**：若使用 macOS / Linux 且 `python` 命令不可用，请使用 `python3 main.py`。

---

## ⚙️ 飞书后台配置

### 开启能力

- 开启 **机器人能力** 并发布版本

### 机器人名称建议

| 配置项 | 建议值 |
|-------|-------|
| 机器人名称 | `共同空闲时间查询` |

> **提示**：项目默认按该名称在被 @ 成员中识别并排除机器人自身。若使用其他名称，请同步修改 [main.py](main.py) 中的 `BOT_DISPLAY_NAME`。

### 订阅事件

| 事件 | 说明 |
|------|------|
| `im.message.receive_v1` | 接收消息 v2.0 |
| `im.chat.access_event.bot_p2p_chat_entered_v1` | 用户进入与机器人会话 |
| `im.chat.member.bot.added_v1` | 机器人进群 |

> 推荐使用 **长连接方式** 接收事件。

### 权限配置（JSON 批量导入）

导入位置：**应用配置 → 开发配置 → 权限管理 → 批量导入/导出权限 → 导入**

<details>
<summary>📋 点击展开权限 JSON</summary>

```json
{
  "scopes": {
    "tenant": [
      "calendar:calendar",
      "calendar:calendar.free_busy:read",
      "calendar:calendar:readonly",
      "contact:user.employee_id:readonly",
      "im:chat:readonly",
      "im:message",
      "im:message.group_at_msg:readonly",
      "im:message.p2p_msg:readonly",
      "im:message.reactions:write_only",
      "im:message:recall",
      "im:message:send_as_bot"
    ],
    "user": [
      "calendar:calendar",
      "calendar:calendar.free_busy:read",
      "calendar:calendar:readonly",
      "contact:user.employee_id:readonly",
      "im:message"
    ]
  }
}
```

</details>

---

## 📏 默认查询规则

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 查询窗口 | 7 天 | 从当前时间开始向后查询 |
| 输出范围 | 工作日 | 仅周一至周五 |
| 工作时间 | `08:30 - 17:00` | 每日可用时段 |
| 最小空闲时长 | 15 分钟 | 低于此时长的空闲时段不展示 |

> 可在 `bot/config.py` 的 `Settings` 中调整上述参数。

## 🧮 算法说明

共同空闲时间 = 工作时间窗口 − 所有参与成员忙碌时间的并集

即：先合并所有人的忙碌区间，再取工作时间内的补集，筛选出满足最小时长的空闲段。

## ❓ 常见问题

<details>
<summary><b>Q：运行时提示 <code>缺少 FEISHU_APP_ID 或 FEISHU_APP_SECRET 环境变量</code></b></summary>

请确认已在项目根目录创建 `.env` 文件，并正确填写了 `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET`。参考 [第六步：配置环境变量](#第六步配置环境变量)。

</details>

<details>
<summary><b>Q：<code>python</code> 命令无法识别</b></summary>

- **Windows**：安装 Python 时未勾选"Add Python to PATH"，需重新安装或手动添加到系统环境变量。
- **macOS / Linux**：请尝试使用 `python3` 代替 `python`。

</details>

<details>
<summary><b>Q：<code>pip install</code> 报权限错误</b></summary>

建议使用虚拟环境（参考 [第四步](#第四步创建虚拟环境推荐)），或在命令前添加 `--user` 参数：

```bash
pip install --user -r requirements.txt
```

</details>

<details>
<summary><b>Q：机器人在群聊中没有响应</b></summary>

请检查：
1. 飞书后台是否已开启 **机器人能力** 并发布版本。
2. 是否已正确订阅事件（`im.message.receive_v1` 等）。
3. 是否已配置所需权限并通过审核。
4. 机器人是否已被添加到目标群聊中。

</details>

---

## 🤝 参与贡献

欢迎提交 Issue 和 Pull Request！请先阅读 [贡献指南](CONTRIBUTING.md)。

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE) 开源。
