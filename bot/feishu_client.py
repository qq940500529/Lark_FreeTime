from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import lark_oapi as lark

from .config import Settings
from .scheduler import TimeSlot, parse_rfc3339


@dataclass
class MessageEventContext:
    message_id: str
    chat_id: str
    message_type: str
    sender_open_id: str
    sender_name: str
    mentions: list[dict]


class FeishuService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = lark.Client.builder() \
            .app_id(settings.app_id) \
            .app_secret(settings.app_secret) \
            .log_level(lark.LogLevel.INFO) \
            .build()
        self._cached_bot_open_id: str | None = settings.bot_open_id

    def parse_message_event(self, data: object) -> MessageEventContext:
        payload = self._obj_to_dict(data)
        event = payload.get("event") or {}
        message = event.get("message") or {}
        sender = event.get("sender") or {}
        sender_id = sender.get("sender_id") or {}

        return MessageEventContext(
            message_id=message.get("message_id") or "",
            chat_id=message.get("chat_id") or "",
            message_type=message.get("message_type") or "",
            sender_open_id=sender_id.get("open_id") or "",
            sender_name="",
            mentions=message.get("mentions") or [],
        )

    def extract_chat_id_from_event(self, data: object) -> str:
        payload = self._obj_to_dict(data)
        event = payload.get("event") or {}
        return event.get("chat_id") or ""

    def add_reaction(self, message_id: str, emoji_type: str = "OneSecond") -> str | None:
        body = {"reaction_type": {"emoji_type": emoji_type}}
        response = self._request(
            method=lark.HttpMethod.POST,
            uri=f"/open-apis/im/v1/messages/{message_id}/reactions",
            body=body,
        )
        return ((response.get("data") or {}).get("reaction_id"))

    def delete_reaction(self, message_id: str, reaction_id: str) -> None:
        self._request(
            method=lark.HttpMethod.DELETE,
            uri=f"/open-apis/im/v1/messages/{message_id}/reactions/{reaction_id}",
        )

    def send_text_to_chat(self, chat_id: str, text: str) -> str:
        body = {
            "receive_id": chat_id,
            "msg_type": "text",
            "content": json.dumps({"text": text}, ensure_ascii=False),
            "uuid": str(uuid.uuid4()),
        }

        response = self._request(
            method=lark.HttpMethod.POST,
            uri="/open-apis/im/v1/messages",
            queries=[("receive_id_type", "chat_id")],
            body=body,
        )
        return (((response or {}).get("data") or {}).get("message_id")) or ""

    def send_markdown_card_to_chat(self, chat_id: str, title: str, markdown: str) -> str:
        card = {
            "config": {
                "wide_screen_mode": True,
                "enable_forward": True,
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": title,
                }
            },
            "elements": [
                {
                    "tag": "markdown",
                    "content": markdown,
                }
            ],
        }
        body = {
            "receive_id": chat_id,
            "msg_type": "interactive",
            "content": json.dumps(card, ensure_ascii=False),
            "uuid": str(uuid.uuid4()),
        }

        response = self._request(
            method=lark.HttpMethod.POST,
            uri="/open-apis/im/v1/messages",
            queries=[("receive_id_type", "chat_id")],
            body=body,
        )
        return (((response or {}).get("data") or {}).get("message_id")) or ""

    def send_post_markdown_to_chat(self, chat_id: str, title: str, markdown: str) -> str:
        content = {
            "zh_cn": {
                "title": title,
                "content": [[{"tag": "md", "text": markdown}]],
            }
        }
        body = {
            "receive_id": chat_id,
            "msg_type": "post",
            "content": json.dumps(content, ensure_ascii=False),
            "uuid": str(uuid.uuid4()),
        }

        response = self._request(
            method=lark.HttpMethod.POST,
            uri="/open-apis/im/v1/messages",
            queries=[("receive_id_type", "chat_id")],
            body=body,
        )
        return (((response or {}).get("data") or {}).get("message_id")) or ""

    def query_batch_freebusy(
        self,
        user_open_ids: list[str],
        timezone: str,
        lookahead_days: int,
    ) -> dict[str, list[TimeSlot]]:
        now = datetime.now().astimezone()
        time_min = now.isoformat(timespec="seconds")
        time_max = (now + timedelta(days=lookahead_days)).isoformat(timespec="seconds")

        body = {
            "time_min": time_min,
            "time_max": time_max,
            "user_ids": user_open_ids,
            "include_external_calendar": True,
            "only_busy": True,
            "need_rsvp_status": False,
        }

        response = self._request(
            method=lark.HttpMethod.POST,
            uri="/open-apis/calendar/v4/freebusy/batch",
            queries=[("user_id_type", "open_id")],
            body=body,
        )

        busy_by_user: dict[str, list[TimeSlot]] = {uid: [] for uid in user_open_ids}
        freebusy_lists = ((response or {}).get("data") or {}).get("freebusy_lists") or []

        for item in freebusy_lists:
            user_id = item.get("user_id")
            if not user_id:
                continue
            intervals: list[TimeSlot] = []
            for fb in item.get("freebusy_items") or []:
                start = fb.get("start_time")
                end = fb.get("end_time")
                if not start or not end:
                    continue
                intervals.append(
                    TimeSlot(
                        start=parse_rfc3339(start, timezone),
                        end=parse_rfc3339(end, timezone),
                    )
                )
            busy_by_user[user_id] = intervals

        return busy_by_user

    def get_bot_open_id(self) -> str | None:
        if self._cached_bot_open_id:
            return self._cached_bot_open_id

        try:
            response = self._request(
                method=lark.HttpMethod.GET,
                uri="/open-apis/bot/v3/info",
            )
            open_id = (((response or {}).get("data") or {}).get("open_id"))
            if open_id:
                self._cached_bot_open_id = open_id
        except Exception:
            return None

        return self._cached_bot_open_id

    @staticmethod
    def build_mention_text(user_open_id: str, body: str) -> str:
        return f'<at user_id="{user_open_id}">你</at> {body}'

    @staticmethod
    def _obj_to_dict(obj: object) -> dict[str, Any]:
        if obj is None:
            return {}
        serialized = lark.JSON.marshal(obj)
        return json.loads(serialized or "{}")

    def _request(
        self,
        method: lark.HttpMethod,
        uri: str,
        queries: list[tuple[str, str]] | None = None,
        body: dict | None = None,
    ) -> dict[str, Any]:
        request = lark.BaseRequest.builder() \
            .http_method(method) \
            .uri(uri) \
            .token_types({lark.AccessTokenType.TENANT}) \
            .queries(queries or []) \
            .body(body or {}) \
            .build()

        response = self.client.request(request)

        if response.code != 0:
            raise RuntimeError(
                f"请求失败 uri={uri}, code={response.code}, msg={response.msg}, log_id={response.get_log_id()}"
            )

        if response.raw and isinstance(response.raw.content, (bytes, bytearray)):
            payload = json.loads(response.raw.content.decode("utf-8"))
            if payload.get("code") != 0:
                raise RuntimeError(
                    f"请求失败 uri={uri}, code={payload.get('code')}, msg={payload.get('msg')}"
                )
            return payload

        return {}
