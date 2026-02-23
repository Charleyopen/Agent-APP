# AgentChat

单页 **Agent 聊天**：一个大模型 + **Mem0 记忆** + **RAG 适配层** + **可扩展 Skills**，架构类似 OpenClaw（Brain + Memory + Hands）。

---

## 功能

- **一个界面**：仅一个聊天页，输入消息、获得回复。
- **连接大模型**：OpenAI 或任意 OpenAI 兼容 API（Azure、Ollama 等）。
- **Mem0 记忆**：持久化用户上下文，对话中自动检索与写入。
- **RAG 适配**：统一检索接口，可接 UltraRAG 或自建向量库。
- **可扩展 Skills**：OpenClaw 风格工具注册，内置时间、计算器，可自定义扩展。

---

## 项目结构

```
AgentChat/
├── main.py           # FastAPI 入口，/api/chat、/、/health
├── config.py         # 环境变量配置
├── agent.py          # Agent 编排：LLM + Memory + RAG + Skills
├── memory.py         # Mem0 封装
├── rag.py            # RAG 适配层（可接 UltraRAG）
├── skills/           # 可扩展 Skills
│   ├── registry.py  # 注册表与执行
│   └── builtin.py    # 内置：get_time、calculator
├── static/
│   ├── index.html    # 单页聊天 UI
│   ├── style.css
│   └── app.js
├── requirements.txt
├── .env.example
└── README.md
```

---

## 快速开始

### 1. 安装依赖

```bash
cd AgentChat
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`，至少配置其一：

- **OpenAI**：`OPENAI_API_KEY=sk-xxx`
- **Ollama**：`OPENAI_BASE_URL=http://localhost:11434/v1`，`LLM_MODEL=llama3.2`（或你本地模型名）

### 3. 启动

```bash
uvicorn main:app --host 0.0.0.0 --port 8765
```

浏览器打开 **http://localhost:8765** 即可使用聊天界面。

---

## API

- `POST /api/chat`  
  - Body: `{ "message": "用户输入", "user_id": "default", "history": [] }`  
  - 返回: `{ "reply": "助手回复" }`
- `GET /health`  
  - 返回: `{ "status": "ok", "service": "AgentChat" }`
- `GET /api/admin/status`  
  - 后台看板用：返回服务、LLM、Mem0、RAG、Skills、统计等状态（JSON）
- **后台看板**：浏览器打开 **http://localhost:8765/admin** 可查看运行状态与统计

---

## 扩展

### 新增 Skill

在 `skills/` 下新增模块，或在 `skills/builtin.py` 中仿照 `register_skill` 注册：

```python
from skills.registry import register_skill

def my_handler(query: str) -> str:
    return "结果"

register_skill(
    "my_skill",
    "描述给 LLM 看",
    {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
    my_handler,
)
```

在 `skills/__init__.py` 中 `register_builtin_skills()` 之后调用你的注册函数，或在该处统一导入。

### 接入 UltraRAG

在 `rag.py` 的 `rag_retrieve()` 中改为调用 UltraRAG 的 Retriever（或 MCP Client），保持「输入 query、返回文档列表」的接口即可。

### 关闭 Mem0

环境变量：`MEM0_ENABLED=false`，Agent 仍可正常运行，仅无持久记忆。

---

## 许可与使用

本模块为示例/原型，可按项目需要修改或二次封装。
