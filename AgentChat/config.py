# -*- coding: utf-8 -*-
"""AgentChat 配置：从环境变量读取，商业级可配置。"""
import os

# LLM：OpenAI 兼容（OpenAI / Azure / Ollama 等）
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "").strip() or None  # Ollama: http://localhost:11434/v1
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")
# 单次 LLM 调用超时（秒），防止外部 API 无响应拖垮请求
LLM_TIMEOUT_SECONDS = int(os.environ.get("LLM_TIMEOUT_SECONDS", "60"))
# 单次 Mem0 检索/写入超时（秒）
MEM0_TIMEOUT_SECONDS = int(os.environ.get("MEM0_TIMEOUT_SECONDS", "10"))
# 整次 /api/chat 请求超时（秒），含多轮 tool 与记忆
CHAT_REQUEST_TIMEOUT_SECONDS = int(os.environ.get("CHAT_REQUEST_TIMEOUT_SECONDS", "120"))

# Mem0 记忆（可选）
MEM0_ENABLED = os.environ.get("MEM0_ENABLED", "true").lower() in ("true", "1", "yes")

# RAG：是否启用、知识库路径（可选，用于简单 RAG）
RAG_ENABLED = os.environ.get("RAG_ENABLED", "false").lower() in ("true", "1", "yes")
RAG_TOP_K = int(os.environ.get("RAG_TOP_K", "3"))

# 服务
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8765"))

# CORS：生产建议配置为前端域名，逗号分隔；留空或 * 表示允许所有
CORS_ORIGINS_RAW = os.environ.get("CORS_ORIGINS", "*").strip()
CORS_ORIGINS = [o.strip() for o in CORS_ORIGINS_RAW.split(",") if o.strip()] if CORS_ORIGINS_RAW != "*" else ["*"]

# 聊天限流：每 key（user_id 或 IP）每分钟最多消息数，0 表示不限制
RATE_LIMIT_CHAT_PER_MIN = int(os.environ.get("RATE_LIMIT_CHAT_PER_MIN", "20"))

# 后台看板鉴权：设置后 /admin、/monitor、/api/admin/status、/api/monitor/aggregate 需带 X-Admin-API-Key
ADMIN_API_KEY = os.environ.get("ADMIN_API_KEY", "").strip()

# 统一监控台：用户注册接口的 base URL，配置后监控台会聚合该服务状态（如 http://localhost:8000 或 Docker 内 http://user-reg-app:8000）
MONITOR_USER_REG_URL = os.environ.get("MONITOR_USER_REG_URL", "").strip()

# 请求体限制
CHAT_MESSAGE_MAX_LENGTH = int(os.environ.get("CHAT_MESSAGE_MAX_LENGTH", "8192"))
CHAT_HISTORY_MAX_ITEMS = int(os.environ.get("CHAT_HISTORY_MAX_ITEMS", "50"))
