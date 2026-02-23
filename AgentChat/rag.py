# -*- coding: utf-8 -*-
"""
RAG 适配层：统一检索接口，可替换为 UltraRAG 或其它实现。
当前为简单内存检索；生产可接 UltraRAG MCP / 向量库。
"""
import logging
from typing import List

from config import RAG_ENABLED, RAG_TOP_K

logger = logging.getLogger(__name__)

# 简单内存知识库：可替换为 Chroma / Milvus / UltraRAG 等
_docs: List[str] = []


def rag_doc_count() -> int:
    """当前知识库文档条数（供看板展示）。"""
    return len(_docs)


def rag_add_docs(texts: List[str]) -> None:
    """向知识库添加文档（简单实现仅做列表存储）。"""
    global _docs
    _docs.extend(texts)
    logger.info("RAG 知识库当前共 %s 条", len(_docs))


def rag_retrieve(query: str, top_k: int = None) -> List[str]:
    """
    根据 query 检索相关文档。
    简单实现：若已配置向量检索则用向量，否则返回前 top_k 条或空。
    可在此处接入 UltraRAG 的 Retriever MCP 或本地向量库。
    """
    if not RAG_ENABLED:
        return []
    k = top_k or RAG_TOP_K
    # 占位：无向量模型时返回空；接入 UltraRAG 时调用其 retriever
    # 示例：return ultrarag_retrieve(query, top_k=k)
    if not _docs:
        return []
    # 简单回退：返回前 k 条（实际应做 embedding 相似度）
    return _docs[:k]


def get_rag_context(query: str) -> str:
    """获取 RAG 上下文字符串，供拼进 prompt。"""
    chunks = rag_retrieve(query)
    if not chunks:
        return ""
    return "参考知识库：\n" + "\n".join(f"- {c}" for c in chunks)
