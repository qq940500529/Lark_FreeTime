from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone as dt_timezone
from zoneinfo import ZoneInfo


@dataclass(frozen=True)
class TimeSlot:
    start: datetime
    end: datetime

    @property
    def duration_minutes(self) -> int:
        return int((self.end - self.start).total_seconds() // 60)


def _merge_intervals(intervals: list[TimeSlot]) -> list[TimeSlot]:
    if not intervals:
        return []

    ordered = sorted(intervals, key=lambda x: x.start)
    merged: list[TimeSlot] = [ordered[0]]

    for current in ordered[1:]:
        last = merged[-1]
        if current.start <= last.end:
            merged[-1] = TimeSlot(start=last.start, end=max(last.end, current.end))
        else:
            merged.append(current)

    return merged


def _complement(day_start: datetime, day_end: datetime, busy: list[TimeSlot]) -> list[TimeSlot]:
    free: list[TimeSlot] = []
    cursor = day_start

    for slot in busy:
        if slot.start > cursor:
            free.append(TimeSlot(start=cursor, end=slot.start))
        cursor = max(cursor, slot.end)

    if cursor < day_end:
        free.append(TimeSlot(start=cursor, end=day_end))

    return free


def _resolve_timezone(timezone: str):
    try:
        return ZoneInfo(timezone)
    except Exception:
        if timezone == "Asia/Shanghai":
            return dt_timezone(timedelta(hours=8), name="Asia/Shanghai")
        return dt_timezone.utc


def _ceil_to_minute(moment: datetime) -> datetime:
    aligned = moment.replace(second=0, microsecond=0)
    if moment.second > 0 or moment.microsecond > 0:
        aligned += timedelta(minutes=1)
    return aligned


def compute_common_free_slots(
    busy_by_user: dict[str, list[TimeSlot]],
    timezone: str,
    work_start_hour: int,
    work_start_minute: int,
    work_end_hour: int,
    work_end_minute: int,
    min_slot_minutes: int,
    lookahead_days: int,
) -> list[TimeSlot]:
    tz = _resolve_timezone(timezone)
    now = _ceil_to_minute(datetime.now(tz))
    today = now.date()

    all_slots: list[TimeSlot] = []
    for offset in range(lookahead_days + 1):
        current_day = today + timedelta(days=offset)
        if current_day.weekday() >= 5:
            continue

        day_start = datetime.combine(
            current_day,
            time(work_start_hour, work_start_minute),
            tzinfo=tz,
        )
        day_end = datetime.combine(
            current_day,
            time(work_end_hour, work_end_minute),
            tzinfo=tz,
        )

        clipped_busy: list[TimeSlot] = []
        for _, user_busy in busy_by_user.items():
            for busy in user_busy:
                start = max(busy.start, day_start)
                end = min(busy.end, day_end)
                if start < end:
                    clipped_busy.append(TimeSlot(start=start, end=end))

        merged_busy = _merge_intervals(clipped_busy)
        day_free = _complement(day_start, day_end, merged_busy)

        for slot in day_free:
            effective_start = max(slot.start, now)
            if effective_start >= slot.end:
                continue
            effective_slot = TimeSlot(start=effective_start, end=slot.end)
            if effective_slot.duration_minutes >= min_slot_minutes:
                all_slots.append(effective_slot)

    return all_slots


def parse_rfc3339(value: str, timezone: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    return parsed.astimezone(_resolve_timezone(timezone))


def format_slots(slots: list[TimeSlot]) -> str:
    if not slots:
        return "未找到满足条件的共同空闲时间。"

    lines = ["共同空闲时间（工作日 08:30-17:00，连续不少于 15 分钟）："]
    for idx, slot in enumerate(slots, 1):
        lines.append(
            f"{idx}. {slot.start:%m-%d %H:%M} ~ {slot.end:%H:%M}（{slot.duration_minutes} 分钟）"
        )

    return "\n".join(lines)


def format_slots_markdown_table(slots: list[TimeSlot]) -> str:
    if not slots:
        return "未找到满足条件的共同空闲时间。"

    weekday_map = {
        0: "周一",
        1: "周二",
        2: "周三",
        3: "周四",
        4: "周五",
        5: "周六",
        6: "周日",
    }

    lines = [
        "```text",
        "日期   星期  开始   结束   时长(分钟)",
        "-----  ----  -----  -----  --------",
    ]

    for slot in slots:
        lines.append(
            f"{slot.start:%m-%d}  {weekday_map[slot.start.weekday()]}  {slot.start:%H:%M}  {slot.end:%H:%M}  {slot.duration_minutes}"
        )

    lines.append("```")

    return "\n".join(lines)
