# -*- coding: utf-8 -*-
"""
Agent 编排：OpenClaw 风格——Brain(LLM) + Memory(Mem0) + RAG + Hands(Skills)。
含超时与稳定性：LLM/Mem0 超时、异常降级，避免单点拖垮请求。
"""
import asyncio
import json
import logging
from typing import Any, List, Optional

from config import (
    LLM_MODEL,
    LLM_TIMEOUT_SECONDS,
    MEM0_TIMEOUT_SECONDS,
    OPENAI_BASE_URL,
    OPENAI_API_KEY,
)
import memory as mem
import rag
from skills import get_tools_for_llm, run_tool, register_builtin_skills

logger = logging.getLogger(__name__)

# 确保内置 Skills 已注册
register_builtin_skills()

SYSTEM_PROMPT = """你是一个有帮助的 AI 助手。你可以使用提供的工具（如查时间、计算）来回答用户。
若对话中涉及用户偏好或重要信息，请自然记住并在后续对话中参考。"""


def _client():
    """OpenAI 兼容客户端（带超时）。"""
    from openai import AsyncOpenAI
    kwargs = {"api_key": OPENAI_API_KEY, "timeout": float(LLM_TIMEOUT_SECONDS)}
    if OPENAI_BASE_URL:
        kwargs["base_url"] = OPENAI_BASE_URL
    return AsyncOpenAI(**kwargs)


async def _call_llm(
    messages: List[dict],
    tools: Optional[List[dict]] = None,
) -> tuple[str, Optional[List[dict]]]:
    """调用 LLM，返回 (content, tool_calls)。带超时，超时抛出 asyncio.TimeoutError。"""
    client = _client()
    kwargs = {"model": LLM_MODEL, "messages": messages}
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"
    resp = await asyncio.wait_for(
        client.chat.completions.create(**kwargs),
        timeout=float(LLM_TIMEOUT_SECONDS),
    )
    choice = resp.choices[0] if resp.choices else None
    if not choice:
        return "", None
    msg = choice.message
    content = (msg.content or "").strip()
    tool_calls = getattr(msg, "tool_calls", None) or []
    return content, tool_calls


async def run_agent(
    user_message: str,
    user_id: str = "default",
    history: Optional[List[dict]] = None,
) -> str:
    """
    单轮 Agent 流程：记忆检索 -> RAG(可选) -> 构造消息 -> LLM(含 Skills) -> 写回记忆 -> 返回回复。
    """
    history = history or []

    # 1) 记忆上下文（带超时，失败则继续无记忆）
    mem_context = ""
    if user_message.strip():
        try:
            mems = await asyncio.wait_for(
                mem.search_memory(user_message, user_id=user_id, limit=5),
                timeout=float(MEM0_TIMEOUT_SECONDS),
            )
            if mems:
                mem_context = "【与当前对话相关的记忆】\n" + "\n".join(mems) + "\n\n"
        except asyncio.TimeoutError:
            logger.warning("Mem0 search 超时，跳过记忆上下文")
        except Exception as e:
            logger.debug("Mem0 search 异常: %s", e)

    # 2) RAG 上下文
    rag_context = rag.get_rag_context(user_message) if user_message.strip() else ""
    if rag_context:
        rag_context = rag_context + "\n\n"

    system = SYSTEM_PROMPT
    if mem_context or rag_context:
        system = system + "\n\n" + mem_context + rag_context

    messages = [{"role": "system", "content": system}]
    for h in history:
        role = h.get("role")
        content = h.get("content", "")
        if role in ("user", "assistant", "system"):
            messages.append({"role": role, "content": content or ""})
    messages.append({"role": "user", "content": user_message})

    tools = get_tools_for_llm()
    max_tool_rounds = 5
    tool_round = 0
    final_content = ""

    while tool_round < max_tool_rounds:
        content, tool_calls = await _call_llm(messages, tools=tools if tool_round == 0 else None)
        if tool_calls:
            for tc in tool_calls:
                name = tc.function.name if hasattr(tc.function, "name") else tc.get("function", {}).get("name")
                args_raw = tc.function.arguments if hasattr(tc.function, "arguments") else tc.get("function", {}).get("arguments", "{}")
                try:
                    args = json.loads(args_raw) if isinstance(args_raw, str) else args_raw
                except json.JSONDecodeError:
                    args = {}
                result = await run_tool(name, args)
                messages.append({
                    "role": "assistant",
                    "content": content or None,
                    "tool_calls": [{"id": getattr(tc, "id", ""), "type": "function", "function": {"name": name, "arguments": args_raw}}],
                })
                messages.append({
                    "role": "tool",
                    "tool_call_id": getattr(tc, "id", ""),
                    "content": result,
                })
            tool_round += 1
            continue
        final_content = content or ""
        break

    if not final_content and tool_round >= max_tool_rounds:
        final_content = "抱歉，本次未能完成回复，请重试。"

    # 写回记忆（带超时，失败不影响返回）
    try:
        await asyncio.wait_for(
            mem.add_memory(
                [{"role": "user", "content": user_message}, {"role": "assistant", "content": final_content}],
                user_id=user_id,
            ),
            timeout=float(MEM0_TIMEOUT_SECONDS),
        )
    except asyncio.TimeoutError:
        logger.warning("Mem0 add 超时，已忽略")
    except Exception as e:
        logger.debug("Mem0 add 异常: %s", e)
    return final_content
