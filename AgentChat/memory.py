# -*- coding: utf-8 -*-
"""Mem0 记忆层：持久化用户上下文，供 Agent 检索。"""
import logging
from typing import List, Optional

from config import MEM0_ENABLED

logger = logging.getLogger(__name__)
_memory = None


def get_memory():
    """获取 Mem0 Memory 实例（懒加载）。未启用或失败时返回 None。"""
    global _memory
    if not MEM0_ENABLED:
        return None
    if _memory is not None:
        return _memory
    try:
        from mem0 import Memory
        _memory = Memory()
        logger.info("Mem0 记忆已初始化")
        return _memory
    except Exception as e:
        logger.warning("Mem0 初始化失败，记忆已禁用: %s", e)
        return None


def get_memory_status() -> dict:
    """供看板展示：是否启用、是否已初始化。"""
    m = get_memory()
    return {"enabled": MEM0_ENABLED, "initialized": m is not None}


async def add_memory(messages: List[dict], user_id: str, metadata: Optional[dict] = None) -> None:
    """将一轮对话写入记忆。"""
    m = get_memory()
    if not m:
        return
    try:
        m.add(messages, user_id=user_id, metadata=metadata or {})
    except Exception as e:
        logger.debug("Mem0 add 失败: %s", e)


async def search_memory(query: str, user_id: str, limit: int = 5) -> List[str]:
    """按查询检索相关记忆，返回文本列表。"""
    m = get_memory()
    if not m:
        return []
    try:
        results = m.search(query=query, user_id=user_id, limit=limit)
        if isinstance(results, dict):
            items = results.get("memories") or results.get("results") or []
        elif isinstance(results, list):
            items = results
        else:
            items = []
        return [r.get("memory", r) if isinstance(r, dict) else str(r) for r in items]
    except Exception as e:
        logger.debug("Mem0 search 失败: %s", e)
        return []


async def get_all_memories(user_id: str) -> List[str]:
    """获取用户全部记忆（用于构造上下文）。"""
    m = get_memory()
    if not m:
        return []
    try:
        results = m.get_all(user_id=user_id)
        if isinstance(results, list):
            return [r.get("memory", r) if isinstance(r, dict) else str(r) for r in results]
        return []
    except Exception as e:
        logger.debug("Mem0 get_all 失败: %s", e)
        return []
