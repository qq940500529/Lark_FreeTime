from __future__ import annotations

import threading

import lark_oapi as lark

from bot.config import load_settings
from bot.feishu_client import FeishuService
from bot.scheduler import compute_common_free_slots, format_slots_markdown_table


settings = load_settings()
service = FeishuService(settings)
processed_message_ids: set[str] = set()
processed_lock = threading.Lock()

USAGE_GUIDE_P2P = (
    "你好，我可以帮你查询共同空闲时间。\n"
    "在与我单聊时，无需 @机器人，只需 @需要参与查询的成员。\n"
    "示例：@张三 @李四"
)

USAGE_GUIDE_GROUP = (
    "你好，我可以帮你查询共同空闲时间。\n"
    "在群聊中请先 @共同空闲时间查询，再 @需要参与查询的成员。\n"
    "示例：@共同空闲时间查询 @张三 @李四"
)

BOT_DISPLAY_NAME = "共同空闲时间查询"


def _extract_target_open_ids(
    mentions: list[dict],
    bot_open_id: str | None,
    bot_display_name: str,
) -> list[str]:
    ids: list[str] = []
    for mention in mentions:
        mention_name = (mention.get("name") or "").strip()
        if mention_name and mention_name == bot_display_name:
            continue

        mention_id = (mention.get("id") or {}).get("open_id")
        if not mention_id:
            continue
        if bot_open_id and mention_id == bot_open_id:
            continue
        if mention_id not in ids:
            ids.append(mention_id)
    return ids


def do_p2_im_message_receive_v1(data: lark.im.v1.P2ImMessageReceiveV1) -> None:
    try:
        ctx = service.parse_message_event(data)
    except Exception as error:
        lark.logger.error(f"解析消息事件失败: {error}")
        return

    with processed_lock:
        if ctx.message_id in processed_message_ids:
            return
        processed_message_ids.add(ctx.message_id)
        if len(processed_message_ids) > 5000:
            processed_message_ids.clear()
            processed_message_ids.add(ctx.message_id)

    one_second_reaction_id: str | None = None
    handled_successfully = False

    try:
        one_second_reaction_id = service.add_reaction(ctx.message_id, "OneSecond")
    except Exception as error:
        lark.logger.warning(f"添加 OneSecond 表情失败: {error}")

    try:
        if ctx.message_type != "text":
            service.send_text_to_chat(
                ctx.chat_id,
                service.build_mention_text(
                    ctx.sender_open_id,
                    "目前仅支持文本消息触发，请在消息中 @ 需要查询的成员。",
                ),
            )
            handled_successfully = True
            return

        bot_open_id = service.get_bot_open_id()
        target_open_ids = _extract_target_open_ids(
            ctx.mentions,
            bot_open_id,
            BOT_DISPLAY_NAME,
        )

        if not target_open_ids:
            service.send_text_to_chat(
                ctx.chat_id,
                service.build_mention_text(
                    ctx.sender_open_id,
                    "未识别到可查询的 @ 成员（已自动排除机器人），请至少 @ 1 位成员。",
                ),
            )
            handled_successfully = True
            return

        busy_by_user = service.query_batch_freebusy(
            user_open_ids=target_open_ids,
            timezone=settings.timezone,
            lookahead_days=settings.lookahead_days,
        )

        slots = compute_common_free_slots(
            busy_by_user=busy_by_user,
            timezone=settings.timezone,
            work_start_hour=settings.work_start_hour,
            work_start_minute=settings.work_start_minute,
            work_end_hour=settings.work_end_hour,
            work_end_minute=settings.work_end_minute,
            min_slot_minutes=settings.min_slot_minutes,
            lookahead_days=settings.lookahead_days,
        )

        table_markdown = format_slots_markdown_table(slots)
        markdown = (
            f"<at user_id=\"{ctx.sender_open_id}\">你</at> 已查询到 {len(target_open_ids)} 位成员的共同空闲时间。\n"
            "\n"
            "**查询范围**：近七天工作日 08:30-17:00，连续空闲不少于 15 分钟\n"
            "\n"
            f"{table_markdown}"
        )
        service.send_post_markdown_to_chat(
            ctx.chat_id,
            "共同空闲时间查询结果",
            markdown,
        )
        handled_successfully = True

    except Exception as error:
        lark.logger.error(f"处理消息失败: {error}")
        try:
            service.send_text_to_chat(
                ctx.chat_id,
                service.build_mention_text(
                    ctx.sender_open_id,
                    f"查询失败：{error}",
                ),
            )
        except Exception as inner_error:
            lark.logger.error(f"发送失败提示消息失败: {inner_error}")
    finally:
        target_emoji = "DONE" if handled_successfully else "EMBARRASSED"
        try:
            if one_second_reaction_id:
                service.delete_reaction(ctx.message_id, one_second_reaction_id)
        except Exception as error:
            lark.logger.warning(f"删除 OneSecond 表情失败: {error}")

        try:
            service.add_reaction(ctx.message_id, target_emoji)
        except Exception as error:
            lark.logger.warning(f"添加 {target_emoji} 表情失败: {error}")


def _send_usage_guide(chat_id: str, guide_text: str) -> None:
    if not chat_id:
        return
    service.send_text_to_chat(chat_id, guide_text)


def do_p2_im_chat_access_event_bot_p2p_chat_entered_v1(
    data: lark.im.v1.P2ImChatAccessEventBotP2pChatEnteredV1,
) -> None:
    try:
        chat_id = service.extract_chat_id_from_event(data)
        _send_usage_guide(chat_id, USAGE_GUIDE_P2P)
    except Exception as error:
        lark.logger.warning(f"处理 p2p 进入会话事件失败: {error}")


def do_p2_im_chat_member_bot_added_v1(data: lark.im.v1.P2ImChatMemberBotAddedV1) -> None:
    try:
        chat_id = service.extract_chat_id_from_event(data)
        _send_usage_guide(chat_id, USAGE_GUIDE_GROUP)
    except Exception as error:
        lark.logger.warning(f"处理机器人入群事件失败: {error}")


# 长连接事件处理器
event_handler = lark.EventDispatcherHandler.builder("", "") \
    .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1) \
    .register_p2_im_chat_access_event_bot_p2p_chat_entered_v1(do_p2_im_chat_access_event_bot_p2p_chat_entered_v1) \
    .register_p2_im_chat_member_bot_added_v1(do_p2_im_chat_member_bot_added_v1) \
    .build()


def main() -> None:
    client = lark.ws.Client(
        settings.app_id,
        settings.app_secret,
        event_handler=event_handler,
        log_level=lark.LogLevel.INFO,
    )
    client.start()


if __name__ == "__main__":
    main()
