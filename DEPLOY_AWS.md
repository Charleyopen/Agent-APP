# 在 AWS 服务器上运行 Vibecoding 全栈

本指南帮助你在**一台 AWS EC2（或其它 Linux 服务器）**上部署并运行整个项目：**用户注册接口**（端口 8000）+ **AgentChat**（端口 8765）。

---

## 一、准备 AWS 服务器

### 1.1 创建 / 使用 EC2 实例

- 登录 [AWS 控制台](https://console.aws.amazon.com/) → EC2 → 启动实例。
- 系统选 **Ubuntu 22.04** 或 **Amazon Linux 2023**。
- 实例类型：**t2.small** 或以上（跑两个服务建议 1GB+ 内存）。
- 存储：默认 8GB 即可。
- **安全组**（必做）：
  - 放行 **22**（SSH）。
  - 放行 **8000**（用户注册 API）。
  - 放行 **8765**（AgentChat 聊天 + 后台看板）。
  - 若用 Nginx 做 80 反向代理，再放行 **80**。
- 下载并保管好 **.pem** 密钥。

### 1.2 访问地址

- 用户注册 API：`http://公网IP:8000`
- AgentChat 聊天页：`http://公网IP:8765`
- AgentChat 后台看板：`http://公网IP:8765/admin`

---

## 二、SSH 登录服务器

本机执行（替换为你的密钥和 IP）：

```bash
chmod 400 你的密钥.pem
ssh -i 你的密钥.pem ubuntu@公网IP
```

Amazon Linux 用户名为 `ec2-user`：

```bash
ssh -i 你的密钥.pem ec2-user@公网IP
```

---

## 三、安装 Docker 与 Docker Compose

### Ubuntu 22.04

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo usermod -aG docker $USER
```

登出再登录（或 `newgrp docker`）后执行：

```bash
docker --version
docker compose version
```

### Amazon Linux 2023

```bash
sudo yum update -y
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

登出再登录后执行 `docker compose version` 确认可用。

---

## 四、把项目放到服务器上

### 方式 A：Git 克隆（推荐）

若项目已在 GitHub/GitLab：

```bash
cd ~
git clone https://你的仓库地址 vibecoding
cd vibecoding
```

### 方式 B：本机 SCP 上传

在本机项目根目录（Vibecoding 所在目录）执行：

```bash
scp -i 你的密钥.pem -r User_Registeration AgentChat docker-compose.aws.yml ubuntu@公网IP:~/vibecoding/
```

然后 SSH 到服务器：

```bash
mkdir -p ~/vibecoding
# 若已用 SCP 上传到别处，再 mv 到 ~/vibecoding
cd ~/vibecoding
```

---

## 五、配置环境变量

在服务器上进入项目根目录，创建 `.env`（必填项请改成你的值）：

```bash
cd ~/vibecoding

cat > .env << 'EOF'
# 用户注册接口（必填）
SECRET_KEY=请改成随机长字符串

# AgentChat：二选一或都填
OPENAI_API_KEY=sk-你的OpenAI密钥
# 使用 Ollama 时可不填 KEY，只填下面两行
# OPENAI_BASE_URL=http://host.docker.internal:11434/v1
# LLM_MODEL=llama3.2

# 可选
# LLM_MODEL=gpt-4o-mini
# MEM0_ENABLED=true
# RAG_ENABLED=false
EOF

# 编辑 SECRET_KEY 和 OPENAI_API_KEY
nano .env
```

说明：

- **SECRET_KEY**：用户注册接口的 JWT 密钥，生产环境务必改成随机长字符串。
- **OPENAI_API_KEY**：AgentChat 调大模型用；用 OpenAI 必填。
- **OPENAI_BASE_URL**：若用 Ollama 等兼容 API，填地址。在 Docker 内访问**宿主机**上的 Ollama：Mac/Windows 可用 `http://host.docker.internal:11434/v1`；Linux 需在 `docker-compose.aws.yml` 里给 `agentchat` 增加 `extra_hosts: - "host.docker.internal:host-gateway"`，或此处直接填宿主机内网 IP（如 `http://172.17.0.1:11434/v1`）。

---

## 六、构建并启动全栈

在项目根目录执行：

```bash
cd ~/vibecoding
docker compose -f docker-compose.aws.yml up -d --build
```

首次会拉取镜像并构建两个应用，稍等 1～2 分钟。检查状态：

```bash
docker compose -f docker-compose.aws.yml ps
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:8765/health
```

若返回 `{"status":"ok",...}` 说明两个服务都正常。

---

## 七、从本机访问

在**你本机**浏览器或终端：

| 服务           | 地址                         |
|----------------|------------------------------|
| 用户注册 API   | `http://公网IP:8000`         |
| API 文档       | `http://公网IP:8000/docs`    |
| AgentChat 聊天 | `http://公网IP:8765`         |
| AgentChat 看板 | `http://公网IP:8765/admin`   |

若打不开，请检查：

1. **安全组**：已放行 8000、8765（来源 `0.0.0.0/0` 或你的 IP）。
2. **服务器防火墙**（若开了 ufw）：
   ```bash
   sudo ufw allow 8000
   sudo ufw allow 8765
   sudo ufw reload
   ```

---

## 八、可选：Nginx 反向代理（80 端口）

若希望用 `http://公网IP` 或域名访问，可在同一台机装 Nginx，把不同路径转到不同服务。

```bash
sudo apt-get install -y nginx   # Ubuntu
# 或 sudo yum install -y nginx  # Amazon Linux
```

示例：根路径给 AgentChat，`/user-api/` 给用户注册接口（需改用户注册应用根路径或 Nginx 配置）。下面为**根路径 → AgentChat、/user-api/ → 8000** 的写法：

```bash
sudo tee /etc/nginx/sites-available/vibecoding << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8765;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /user-api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF
sudo ln -sf /etc/nginx/sites-available/vibecoding /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

安全组放行 **80** 后，用 `http://公网IP` 访问 AgentChat；用户注册 API 需通过 `http://公网IP/user-api/` 访问（前端若接该 API，需把 base URL 改为 `http://公网IP/user-api`）。

若只代理一个服务，可简化为只写一个 `location /` 指向 8765 或 8000。

---

## 九、常用运维命令（在服务器上）

```bash
cd ~/vibecoding

# 查看所有容器状态
docker compose -f docker-compose.aws.yml ps

# 查看 AgentChat 日志
docker compose -f docker-compose.aws.yml logs -f agentchat

# 查看用户注册接口日志
docker compose -f docker-compose.aws.yml logs -f user-reg-app

# 停止全栈
docker compose -f docker-compose.aws.yml down

# 再次启动（数据与卷保留）
docker compose -f docker-compose.aws.yml up -d

# 仅重启 AgentChat
docker compose -f docker-compose.aws.yml restart agentchat
```

按以上步骤完成后，整个项目已在 AWS 上运行，可直接用公网 IP（或配置的域名）访问用户注册 API 与 AgentChat。
