# -*- coding: utf-8 -*-
"""可扩展 Skills：OpenClaw 风格工具注册与执行。"""
from skills.registry import get_tools_for_llm, run_tool, register_skill
from skills.builtin import register_builtin_skills

__all__ = ["get_tools_for_llm", "run_tool", "register_skill", "register_builtin_skills"]
