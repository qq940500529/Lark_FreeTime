from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_id: str
    app_secret: str
    timezone: str = "Asia/Shanghai"
    work_start_hour: int = 8
    work_start_minute: int = 30
    work_end_hour: int = 17
    work_end_minute: int = 0
    min_slot_minutes: int = 15
    lookahead_days: int = 7
    bot_open_id: str | None = None


def load_settings() -> Settings:
    app_id = os.getenv("FEISHU_APP_ID", "").strip()
    app_secret = os.getenv("FEISHU_APP_SECRET", "").strip()
    bot_open_id = os.getenv("FEISHU_BOT_OPEN_ID", "").strip() or None

    if not app_id or not app_secret:
        raise ValueError("缺少 FEISHU_APP_ID 或 FEISHU_APP_SECRET 环境变量")

    return Settings(
        app_id=app_id,
        app_secret=app_secret,
        bot_open_id=bot_open_id,
    )
