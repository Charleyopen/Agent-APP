#!/bin/bash
# 推送整个 Vibecoding 到 https://github.com/Charleyopen/Agent-APP
set -e
cd "$(dirname "$0")"

if [ -d .git ] && [ -f .git/HEAD ]; then
  echo ">>> 已有 .git，检查 remote..."
  if git remote get-url origin 2>/dev/null; then
    git remote set-url origin https://github.com/Charleyopen/Agent-APP.git
  else
    git remote add origin https://github.com/Charleyopen/Agent-APP.git
  fi
else
  echo ">>> 初始化仓库并添加 remote..."
  git init
  git remote add origin https://github.com/Charleyopen/Agent-APP.git
fi

echo ""
echo ">>> 添加并提交..."
git add -A
if git diff --cached --quiet; then
  echo "无新变更。若要强制推送: git push -u origin main"
  exit 0
fi
git commit -m "chore: Vibecoding full stack (User_Registeration, AgentChat, Self_Center, deploy)"
git branch -M main

echo ""
echo ">>> 推送到 origin main..."
git push -u origin main

echo ""
echo "完成: https://github.com/Charleyopen/Agent-APP"
