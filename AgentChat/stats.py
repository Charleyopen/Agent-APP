# -*- coding: utf-8 -*-
"""运行状态统计：供后台看板展示。"""
import time
from typing import Any, Dict

_started_at = time.time()
_chat_total = 0
_chat_errors = 0
_last_activity_at: float = 0


def record_chat_success() -> None:
    global _chat_total, _last_activity_at
    _chat_total += 1
    _last_activity_at = time.time()


def record_chat_error() -> None:
    global _chat_total, _chat_errors, _last_activity_at
    _chat_total += 1
    _chat_errors += 1
    _last_activity_at = time.time()


def get_stats() -> Dict[str, Any]:
    return {
        "chat_total": _chat_total,
        "chat_errors": _chat_errors,
        "last_activity_at": _last_activity_at if _last_activity_at else None,
        "uptime_seconds": max(0, time.time() - _started_at),
        "started_at": _started_at,
    }
