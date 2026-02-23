# -*- coding: utf-8 -*-
"""内置 Skills：时间、计算器等。"""
from datetime import datetime, timezone
from skills.registry import register_skill


def _get_time(*, timezone_name: str = "UTC") -> str:
    tz = timezone.utc
    try:
        import zoneinfo
        tz = zoneinfo.ZoneInfo(timezone_name)
    except Exception:
        pass
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")


def _calculator(expression: str) -> str:
    """安全计算：仅允许数字与 +-*/.() 空格。"""
    allowed = set("0123456789+-*/.() ")
    if not all(c in allowed for c in expression):
        return "仅支持数字与 + - * / ( )"
    try:
        return str(eval(expression))
    except Exception as e:
        return f"计算错误: {e}"


def register_builtin_skills() -> None:
    register_skill(
        "get_time",
        "获取当前日期时间，可指定时区，如 Asia/Shanghai、UTC",
        {"type": "object", "properties": {"timezone_name": {"type": "string", "description": "时区名"}}, "required": []},
        lambda timezone_name="UTC": _get_time(timezone_name=timezone_name or "UTC"),
    )
    register_skill(
        "calculator",
        "计算数学表达式，例如 1+2*3、2*(3+4)",
        {"type": "object", "properties": {"expression": {"type": "string", "description": "数学表达式"}}, "required": ["expression"]},
        lambda expression: _calculator(expression=expression),
    )
