# Vibecoding 项目维护指南

面向接手人的维护与提测说明，便于持续迭代与问题排查。

---

## 一、项目结构概览

```
Vibecoding/
├── User_Registeration/     # 用户注册与登录 API（FastAPI + PostgreSQL + Redis）
│   ├── miniapi/            # 核心包：路由、安全、缓存、限流、中间件
│   ├── server.py           # 启动入口
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml  # 单模块本地/测试用
├── AgentChat/              # Agent 聊天（LLM + Mem0 + RAG + Skills）
│   ├── main.py             # FastAPI 入口
│   ├── agent.py            # 编排：LLM、记忆、RAG、工具
│   ├── memory.py           # Mem0 封装
│   ├── rag.py              # RAG 适配层
│   ├── skills/             # 可扩展 Skills
│   ├── static/             # 聊天页 + 后台看板
│   ├── requirements.txt
│   └── Dockerfile
├── Self_Center/            # 个人中心 H5 静态资源（可由 Nginx/任意静态服务提供）
├── docs/                   # 文档与合规
│   ├── MAINTENANCE.md      # 本文件
│   ├── PRIVACY.md
│   └── TERMS.md
├── docker-compose.aws.yml  # 全栈一键部署（用户注册 + AgentChat）
├── DEPLOY_AWS.md           # 部署步骤
├── PRODUCTION_CHECKLIST.md # 上线前检查
├── README.md
└── .env.example             # 根目录环境变量示例
```

---

## 二、技术栈与端口

| 模块 | 技术 | 默认端口 | 说明 |
|------|------|----------|------|
| User_Registeration | FastAPI, asyncpg, Redis, JWT | 8000 | 注册/登录/me/用户列表 |
| AgentChat | FastAPI, OpenAI SDK, Mem0 | 8765 | 聊天、后台看板 /admin |
| PostgreSQL | - | 5432 | 用户数据 |
| Redis | - | 6379 | 用户资料/列表缓存（可选） |

---

## 三、本地运行（开发/自测）

### 3.1 用户注册接口

```bash
cd User_Registeration
cp .env.example .env   # 编辑 DATABASE_URL、SECRET_KEY 等
pip install -r requirements.txt
# 需先启动 PostgreSQL（或 docker compose up -d 只起 db+redis）
python server.py
# 或单进程调试：uvicorn miniapi:app --reload --port 8000
```

- 接口文档：http://127.0.0.1:8000/docs  
- 健康检查：http://127.0.0.1:8000/health 、 http://127.0.0.1:8000/ready  

### 3.2 AgentChat

```bash
cd AgentChat
cp .env.example .env   # 至少配置 OPENAI_API_KEY 或 OPENAI_BASE_URL
pip install -r requirements.txt
python server.py
# 或：uvicorn main:app --reload --port 8765
```

- 聊天页：http://127.0.0.1:8765  
- 后台看板：http://127.0.0.1:8765/admin  
- 健康检查：http://127.0.0.1:8765/health  

### 3.3 全栈 Docker（本地一键）

```bash
# 在 Vibecoding 根目录
cp .env.example .env
# 编辑 .env：SECRET_KEY、OPENAI_API_KEY 等
docker compose -f docker-compose.aws.yml up -d --build
```

---

## 四、环境变量速查

### User_Registeration

| 变量 | 说明 | 默认/示例 |
|------|------|-----------|
| DATABASE_URL | PostgreSQL 连接串 | postgresql://user:pass@host:5432/dbname |
| SECRET_KEY | JWT 签名密钥 | 生产必改 |
| REDIS_URL | Redis 连接串，空则禁用缓存 | redis://localhost:6379/0 |
| CORS_ORIGINS | 允许的前端域名，逗号分隔 | * |
| RATE_LIMIT_AUTH_PER_MIN | 登录/注册每 IP 每分钟次数 | 10 |
| DB_COMMAND_TIMEOUT | 单条 SQL 超时（秒） | 30 |
| REDIS_SOCKET_TIMEOUT | Redis 读写超时（秒） | 5 |

### AgentChat

| 变量 | 说明 | 默认/示例 |
|------|------|-----------|
| OPENAI_API_KEY | OpenAI 或兼容 API 密钥 | sk-xxx |
| OPENAI_BASE_URL | 兼容 API 地址（如 Ollama） | http://localhost:11434/v1 |
| LLM_MODEL | 模型名 | gpt-4o-mini |
| LLM_TIMEOUT_SECONDS | 单次 LLM 调用超时 | 60 |
| MEM0_TIMEOUT_SECONDS | Mem0 检索/写入超时 | 10 |
| CHAT_REQUEST_TIMEOUT_SECONDS | 整次 /api/chat 超时 | 120 |
| ADMIN_API_KEY | 看板鉴权，设置后需带 X-Admin-API-Key | - |
| RATE_LIMIT_CHAT_PER_MIN | 每用户/IP 每分钟消息数 | 20 |

---

## 五、提测指南（测试与发布前检查）

### 5.1 提测前自测清单

- [ ] 本地或测试环境能正常启动（User_Registeration、AgentChat 或全栈 Docker）
- [ ] 环境变量已按测试/生产配置（SECRET_KEY、CORS、限流等）
- [ ] 以下接口与页面至少跑通一遍（见 5.2、5.3）

### 5.2 用户注册接口（提测用例）

| 步骤 | 操作 | 预期 |
|------|------|------|
| 1 | GET http://localhost:8000/health | 200，`{"status":"ok","db":"ok"}` |
| 2 | GET http://localhost:8000/ready | 200，含 db/redis 状态 |
| 3 | POST /api/register，body: `{"username":"test1","password":"123456"}` | 200，返回 `access_token`、`user` |
| 4 | POST /api/register，同上 username | 400，该账号已存在 |
| 5 | POST /api/login，body: `{"username":"test1","password":"123456"}` | 200，返回 `access_token`、`user` |
| 6 | GET /api/me，Header: `Authorization: Bearer <token>` | 200，当前用户信息 |
| 7 | GET /api/me，无 token 或错误 token | 401 |
| 8 | GET /api/users | 200，`{"users":[...]}` |
| 9 | 同一 IP 短时间多次登录/注册 | 超过限流后 429 |

可用 Swagger http://localhost:8000/docs 执行上述请求。

### 5.3 AgentChat 提测用例

| 步骤 | 操作 | 预期 |
|------|------|------|
| 1 | GET http://localhost:8765/health | 200，`{"status":"ok"}` |
| 2 | 浏览器打开 http://localhost:8765 | 聊天页可加载 |
| 3 | 在聊天页发送一条消息 | 返回助手回复（依赖 LLM 配置） |
| 4 | 未配置 OPENAI_API_KEY 且无 OPENAI_BASE_URL 时发送消息 | 503 或明确错误提示 |
| 5 | GET http://localhost:8765/admin | 看板页可加载；若配置 ADMIN_API_KEY，拉取状态需输入 Key |
| 6 | POST /api/chat，body: `{"message":"你好","user_id":"u1"}` | 200，`{"reply":"..."}` |
| 7 | 同一 user_id 短时间大量请求 | 超过限流后 429 |
| 8 | 发送极长消息或长时间不返回的模型 | 在配置超时内返回或 504 超时提示 |

### 5.4 性能与稳定性相关验证（可选）

- 连续 10～20 次注册/登录，无 5xx、连接池无报错
- 连续 5～10 次聊天请求，无 5xx；Mem0/Redis 异常时接口仍可返回（降级）
- 关闭 Redis 后用户注册接口仍可正常登录/注册（仅无缓存）
- 将 LLM 或 Mem0 调慢或不可达，观察超时与错误信息是否符合预期（504/500 及文案）

---

## 六、常见问题与排查

| 现象 | 可能原因 | 处理建议 |
|------|----------|----------|
| 用户注册接口启动报错 | DATABASE_URL 错误或 PostgreSQL 未启动 | 检查 .env、本机或 Docker 内 pg 是否可连 |
| 登录/注册 429 | 触发限流 | 等 1 分钟或调大 RATE_LIMIT_AUTH_PER_MIN |
| AgentChat 503 | 未配置 LLM | 配置 OPENAI_API_KEY 或 OPENAI_BASE_URL |
| 聊天 504 | LLM/网络慢或超时 | 调大 CHAT_REQUEST_TIMEOUT_SECONDS 或 LLM_TIMEOUT_SECONDS；检查模型与网络 |
| 看板 401 | 已配置 ADMIN_API_KEY | 请求头带 X-Admin-API-Key 或在看板页输入 Key |
| push 报错 HTTP2 framing | Git/curl 与 HTTP/2 兼容问题 | 执行 `git config --global http.version HTTP/1.1` 后重试 push |

---

## 七、日志与监控

- **User_Registeration**：日志目录由 `DATA_DIR` 决定，默认写入 `mini.log`；同时输出到控制台。
- **AgentChat**：日志输出到控制台；无单独日志文件时可配合 systemd/容器或 Nginx 记录访问日志。
- **生产建议**：对 /health、/ready 做定时探测；对 5xx、504 做告警；敏感信息勿写入日志。

---

## 八、部署与发布

- 部署步骤见根目录 **DEPLOY_AWS.md**。
- 上线前必做项见 **PRODUCTION_CHECKLIST.md**（SECRET_KEY、ADMIN_API_KEY、CORS、HTTPS 等）。

---

## 九、扩展与修改建议

- **新增 API（用户注册）**：在 `User_Registeration/miniapi/api/routes.py` 增加路由；需鉴权时使用 `Depends(get_current_user)`。
- **新增 Skill（AgentChat）**：在 `AgentChat/skills/` 下注册新工具，参见 `skills/builtin.py` 与 README。
- **调整超时与限流**：通过环境变量修改（见第四节），无需改代码即可调优。

---

本指南与项目同步更新；提测或交接时请以当前仓库的 README、DEPLOY_AWS、PRODUCTION_CHECKLIST 为准。
