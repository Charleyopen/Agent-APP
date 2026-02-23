# 推送整个 Vibecoding 项目到 GitHub

目标仓库：**https://github.com/Charleyopen/Agent-APP**

把 **Vibecoding**（含 User_Registeration、AgentChat、Self_Center、部署与文档）推送到 Agent-APP 仓库。

---

## 一键命令（在终端执行）

```bash
cd /Users/tc/Desktop/02_Learn/Vibecoding

git init
git remote add origin https://github.com/Charleyopen/Agent-APP.git

git add -A
git status
git commit -m "chore: initial commit - Vibecoding full stack (User_Registeration, AgentChat, Self_Center, deploy)"

git branch -M main
git push -u origin main
```

若 push 报错 **Error in the HTTP2 framing layer**，先执行：

```bash
git config --global http.version HTTP/1.1
```

再执行一次 `git push -u origin main`。

---

## 说明

- **User_Registeration** 下的 `.git` 已被根目录 `.gitignore` 排除，整份项目作为单一仓库推送。
- 推送成功后可在 https://github.com/Charleyopen/Agent-APP 查看。
