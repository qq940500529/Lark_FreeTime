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
feishu_kongxianshijian/
├── main.py                 # 长连接事件入口
├── bot/
│   ├── __init__.py         # 包标记
│   ├── config.py           # 配置加载
│   ├── feishu_client.py    # 飞书 API 封装
│   └── scheduler.py        # 共同空闲时间计算
├── requirements.txt        # Python 依赖
├── .env.example            # 环境变量模板
└── .gitignore
```

## 🚀 快速开始

### 1. 环境准备

- Python **3.10** 或更高版本

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制模板并编辑：

```bash
cp .env.example .env
```

填写以下内容（已支持从 `.env` 文件读取）：

```env
FEISHU_APP_ID=你的应用ID
FEISHU_APP_SECRET=你的应用密钥
# 可选：若你已知机器人 open_id，可配置以更稳定地排除机器人
FEISHU_BOT_OPEN_ID=ou_xxx
```

### 4. 运行

```bash
python main.py
```

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

## 🤝 参与贡献

欢迎提交 Issue 和 Pull Request！请先阅读 [贡献指南](CONTRIBUTING.md)。

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE) 开源。
