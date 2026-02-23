# AgentChat 后端 + 静态资源（国内/海外均可构建）
# 国内构建：docker build --build-arg PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple -t agentchat .
FROM python:3.11-slim

WORKDIR /app

ARG PIP_INDEX_URL=
ENV PIP_INDEX_URL=${PIP_INDEX_URL}

COPY requirements.txt .
RUN if [ -n "$PIP_INDEX_URL" ]; then pip install --no-cache-dir -i "$PIP_INDEX_URL" -r requirements.txt; else pip install --no-cache-dir -r requirements.txt; fi

COPY config.py main.py agent.py memory.py rag.py stats.py .
COPY skills ./skills
COPY static ./static
COPY server.py .

ENV TZ=UTC
ENV HOST=0.0.0.0
ENV PORT=8765

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:8765/health || exit 1

EXPOSE 8765
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8765"]
