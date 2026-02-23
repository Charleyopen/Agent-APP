# Vibecoding

可部署的**商业级**产品栈：用户注册与鉴权、个人中心 H5、Agent 聊天（LLM + 记忆 + RAG + Skills），支持 Docker 一键上云。

---

## 产品模块

| 模块 | 说明 | 端口/入口 |
|------|------|-----------|
| **User_Registeration** | 用户注册、登录、JWT、用户列表，PostgreSQL + Redis 缓存 | API `:8000` |
| **Self_Center** | 物联网 APP 个人中心 H5（设置、设备、账号安全等） | 静态资源，由宿主 APP 或 Nginx 提供 |
| **AgentChat** | 单页 Agent 聊天：大模型 + Mem0 记忆 + RAG + 可扩展 Skills | 聊天 `:8765`，看板 `:8765/admin` |

---

## 快速开始

### 本地开发

- **用户注册接口**：`cd User_Registeration && pip install -r requirements.txt && uvicorn miniapi.main:app --reload --port 8000`（需 PostgreSQL，可选 Redis）
- **AgentChat**：`cd AgentChat && pip install -r requirements.txt && uvicorn main:app --reload --port 8765`（需配置 `OPENAI_API_KEY` 或 Ollama）
- **Self_Center**：用浏览器打开 `Self_Center/index.html` 或由任意静态服务器提供

### 生产部署（Docker 一键）

在项目根目录配置 `.env` 后执行：

```bash
docker compose -f docker-compose.aws.yml up -d --build
```

详见 [DEPLOY_AWS.md](./DEPLOY_AWS.md)。上线前请阅读 [PRODUCTION_CHECKLIST.md](./PRODUCTION_CHECKLIST.md)。

---

## 规范与合规

- **API**：错误响应统一为 `{ "success": false, "error": { "code", "message", "request_id" } }`；请求带 `X-Request-ID` 时原样回传，便于排查。
- **安全**：CORS、限流、安全头、Admin 看板鉴权均可配置；生产请务必修改默认 SECRET_KEY / 设置 ADMIN_API_KEY，并阅读 [PRODUCTION_CHECKLIST.md](./PRODUCTION_CHECKLIST.md)。

## 文档

- [DEPLOY_AWS.md](./DEPLOY_AWS.md) — AWS/自建机部署步骤
- [PRODUCTION_CHECKLIST.md](./PRODUCTION_CHECKLIST.md) — 上线前检查清单
- [docs/PRIVACY.md](./docs/PRIVACY.md) — 隐私政策（可对外展示）
- [docs/TERMS.md](./docs/TERMS.md) — 用户协议（可对外展示）

各子模块见各自目录下的 README。

---

## 许可

见 [LICENSE](./LICENSE)（若存在）。可依项目需要选用 MIT / Apache-2.0 等。
