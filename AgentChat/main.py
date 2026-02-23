# -*- coding: utf-8 -*-
"""AgentChat FastAPI 应用：单页聊天 + /chat 接口，商业级中间件与鉴权。"""
import asyncio
import logging
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

from agent import run_agent
from config import (
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    CHAT_REQUEST_TIMEOUT_SECONDS,
    HOST,
    PORT,
    LLM_MODEL,
    MEM0_ENABLED,
    RAG_ENABLED,
    RAG_TOP_K,
    CORS_ORIGINS,
    RATE_LIMIT_CHAT_PER_MIN,
    ADMIN_API_KEY,
    CHAT_MESSAGE_MAX_LENGTH,
    CHAT_HISTORY_MAX_ITEMS,
)
from middleware import RequestIDMiddleware, SecurityHeadersMiddleware
import memory as mem_module
import rag
from rate_limit import is_allowed
from skills.registry import list_skills
from stats import get_stats, record_chat_error, record_chat_success

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def _client_ip(request: Request) -> str:
    xff = request.headers.get("X-Forwarded-For")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _error_response(request: Request, status_code: int, message: str, code: str = None) -> JSONResponse:
    rid = getattr(request.state, "request_id", None) if request else None
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {"code": code or f"HTTP_{status_code}", "message": message, "request_id": rid},
        },
    )


async def require_admin_key(x_admin_api_key: Optional[str] = Header(None, alias="X-Admin-API-Key")):
    """当 ADMIN_API_KEY 已配置时，要求请求头带正确的 X-Admin-API-Key。"""
    if not ADMIN_API_KEY:
        return
    if (x_admin_api_key or "").strip() != ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="需要有效的 Admin API Key")


app = FastAPI(
    title="AgentChat",
    description="单页 Agent 聊天：LLM + Mem0 记忆 + RAG 适配 + 可扩展 Skills（OpenClaw 风格）",
    version="1.0.0",
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return _error_response(request, exc.status_code, detail)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=CHAT_MESSAGE_MAX_LENGTH)
    user_id: str = Field(default="default", max_length=128)
    history: Optional[List[dict]] = None


class ChatResponse(BaseModel):
    reply: str


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: Request, req: ChatRequest):
    limit_key = req.user_id or _client_ip(request)
    if not is_allowed(limit_key, RATE_LIMIT_CHAT_PER_MIN):
        raise HTTPException(status_code=429, detail="发送过于频繁，请稍后再试")
    if not OPENAI_API_KEY and not OPENAI_BASE_URL:
        record_chat_error()
        raise HTTPException(
            status_code=503,
            detail="请配置 OPENAI_API_KEY 或 OPENAI_BASE_URL（如 Ollama）",
        )
    history = (req.history or [])[:CHAT_HISTORY_MAX_ITEMS]
    try:
        reply = await asyncio.wait_for(
            run_agent(
                user_message=req.message,
                user_id=req.user_id,
                history=history,
            ),
            timeout=float(CHAT_REQUEST_TIMEOUT_SECONDS),
        )
        record_chat_success()
        return ChatResponse(reply=reply)
    except asyncio.TimeoutError:
        record_chat_error()
        logger.warning("chat 请求超时 (limit=%ss)", CHAT_REQUEST_TIMEOUT_SECONDS)
        raise HTTPException(
            status_code=504,
            detail="请求处理超时，请稍后重试或缩短输入内容",
        )
    except Exception as e:
        record_chat_error()
        logger.exception("chat 失败: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok", "service": "AgentChat"}


@app.get("/ready")
async def ready():
    """就绪检查：可被负载均衡使用。"""
    return {"status": "ok"}


@app.get("/api/admin/status", dependencies=[Depends(require_admin_key)])
async def admin_status():
    """后台看板：服务、LLM、Mem0、RAG、Skills、统计。"""
    s = get_stats()
    last_at = s.get("last_activity_at")
    return {
        "service": {
            "status": "ok",
            "uptime_seconds": round(s["uptime_seconds"], 1),
            "started_at": s["started_at"],
        },
        "llm": {
            "configured": bool(OPENAI_API_KEY or OPENAI_BASE_URL),
            "base_url": (OPENAI_BASE_URL[:50] + "…") if OPENAI_BASE_URL and len(OPENAI_BASE_URL) > 50 else (OPENAI_BASE_URL or "—"),
            "model": LLM_MODEL,
        },
        "memory": mem_module.get_memory_status(),
        "rag": {
            "enabled": RAG_ENABLED,
            "doc_count": rag.rag_doc_count(),
            "top_k": RAG_TOP_K,
        },
        "skills": list_skills(),
        "stats": {
            "chat_total": s["chat_total"],
            "chat_errors": s["chat_errors"],
            "last_activity_at": last_at,
            "last_activity_iso": (__import__("datetime").datetime.utcfromtimestamp(last_at).isoformat() + "Z") if last_at else None,
        },
    }


# 单页前端：优先从 static 目录提供 index.html
STATIC_DIR = Path(__file__).resolve().parent / "static"
if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/")
    async def index():
        index_file = STATIC_DIR / "index.html"
        if index_file.is_file():
            return FileResponse(index_file)
        return {"message": "AgentChat API", "docs": "/docs"}

    @app.get("/admin")
    async def admin_dashboard():
        admin_file = STATIC_DIR / "admin.html"
        if admin_file.is_file():
            return FileResponse(admin_file)
        return {"message": "Admin dashboard not found", "status_api": "/api/admin/status"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
