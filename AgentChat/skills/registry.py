# -*- coding: utf-8 -*-
"""Skills 注册表：名称 -> (description, parameters_schema, handler)。"""
import logging
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

# name -> (description, json_schema_params, handler)
_skills: Dict[str, tuple] = {}


def register_skill(
    name: str,
    description: str,
    parameters: Optional[Dict[str, Any]] = None,
    handler: Optional[Callable] = None,
):
    """注册一个 Skill（OpenAI 函数调用格式）。"""
    params = parameters or {"type": "object", "properties": {}, "required": []}
    _skills[name] = (description, params, handler)


def list_skills() -> List[Dict[str, Any]]:
    """返回已注册技能列表（名称、描述），供看板展示。"""
    return [{"name": name, "description": desc} for name, (desc, _, _) in _skills.items()]


def get_tools_for_llm() -> List[Dict[str, Any]]:
    """返回 OpenAI 格式的 tools 列表，供 LLM 使用。"""
    out = []
    for name, (desc, schema, _) in _skills.items():
        if isinstance(schema, dict) and "properties" in schema:
            out.append({
                "type": "function",
                "function": {"name": name, "description": desc, "parameters": schema},
            })
        else:
            out.append({
                "type": "function",
                "function": {"name": name, "description": desc, "parameters": {"type": "object", "properties": schema or {}, "required": []}},
            })
    return out


async def run_tool(name: str, arguments: Dict[str, Any]) -> str:
    """执行指定 Skill，返回结果字符串。"""
    if name not in _skills:
        return f"未知技能: {name}"
    _, _, handler = _skills[name]
    if not handler:
        return f"技能 {name} 未实现"
    try:
        import asyncio
        if asyncio.iscoroutinefunction(handler):
            return str(await handler(**arguments))
        return str(handler(**arguments))
    except Exception as e:
        logger.exception("执行技能 %s 失败", name)
        return f"执行失败: {e}"
