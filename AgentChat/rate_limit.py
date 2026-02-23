# -*- coding: utf-8 -*-
"""简单内存限流：按 key 固定窗口计数，供 /api/chat 使用。"""
import time
from typing import Dict, Tuple

# key -> (window_start_ts, count)
_windows: Dict[str, Tuple[float, int]] = {}
_TTL = 120


def _clean() -> None:
    now = time.time()
    expired = [k for k, (start, _) in _windows.items() if now - start > _TTL]
    for k in expired:
        del _windows[k]


def is_allowed(key: str, max_per_minute: int) -> bool:
    if max_per_minute <= 0:
        return True
    now = time.time()
    window_start = int(now // 60) * 60.0
    _clean()
    if key not in _windows:
        _windows[key] = (window_start, 1)
        return True
    start, count = _windows[key]
    if start != window_start:
        _windows[key] = (window_start, 1)
        return True
    if count >= max_per_minute:
        return False
    _windows[key] = (start, count + 1)
    return True
