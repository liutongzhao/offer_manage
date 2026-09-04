#!/bin/zsh
# 投递管理系统 一键启动（screen 常驻，screen 不可用时自动降级 nohup）
# 用法：zsh start.sh        启动/补启所有服务（幂等，已在跑的会跳过）
#       zsh start.sh status 查看状态
#       zsh start.sh stop   全部停止
# 会话名：offer-backend(5112) / offer-frontend(5111)；MinIO 走 docker 容器 offer-minio
# 日志（nohup 降级时）：$BASE/scripts/logs/

BASE="/Users/liutongzhao/WorkBuddy项目/秋招投递/投递管理系统"
LOGDIR="$BASE/scripts/logs"
mkdir -p "$LOGDIR"

# 用 screen 发起后台会话；1 秒后确认会话存在，失败则 nohup 兜底
launch() {
  local name="$1" dir="$2" cmd="$3" log="$4"
  screen -dmS "$name" zsh -c "cd '$dir' && $cmd"
  sleep 1
  if screen -ls 2>/dev/null | grep -q "\.${name}" || screen -ls 2>/dev/null | grep -q "${name}"; then
    echo "  → screen 会话 $name"
  else
    (cd "$dir" && nohup zsh -c "$cmd" >"$log" 2>&1 &)
    echo "  → nohup 兜底（screen 不可用），日志 $log"
  fi
}

start_minio() {
  if docker ps --format '{{.Names}}' | grep -qx offer-minio; then
    echo "MinIO    : 已在运行"
  elif docker ps -a --format '{{.Names}}' | grep -qx offer-minio; then
    docker start offer-minio >/dev/null && echo "MinIO    : 已启动（容器 offer-minio）"
  else
    echo "MinIO    : 容器不存在，请先创建"
  fi
}

start_backend() {
  if curl -s --noproxy '*' -o /dev/null http://127.0.0.1:5112/api/v1/health; then
    echo "后端 5112 : 已在运行"
  else
    echo "后端 5112 : 启动中"
    launch offer-backend "$BASE/backend" "source .venv/bin/activate && exec uvicorn app.main:app --host 0.0.0.0 --port 5112" "$LOGDIR/backend.log"
  fi
}

# 前端存活检测：vite 只绑 IPv6 localhost，127.0.0.1 和 [::1] 都试
fe_alive() {
  curl -s --noproxy '*' -o /dev/null http://127.0.0.1:5111/ || \
  curl -s --noproxy '*' -o /dev/null "http://[::1]:5111/"
}

start_frontend() {
  if fe_alive; then
    echo "前端 5111 : 已在运行"
  else
    echo "前端 5111 : 启动中"
    NODE_BIN="/Users/liutongzhao/.workbuddy/binaries/node/versions/22.22.2-2/bin/node"
    launch offer-frontend "$BASE/frontend" "NODE_OPTIONS='' exec '$NODE_BIN' node_modules/vite/bin/vite.js" "$LOGDIR/frontend.log"
  fi
}

case "$1" in
  stop)
    screen -S offer-backend -X quit 2>/dev/null
    screen -S offer-frontend -X quit 2>/dev/null
    lsof -ti :5111,:5112 | xargs kill 2>/dev/null
    docker stop offer-minio >/dev/null 2>&1
    echo "已全部停止"
    ;;
  status)
    screen -ls | grep -E 'offer-' || echo "无 offer screen 会话"
    lsof -nP -iTCP:5111 -iTCP:5112 -sTCP:LISTEN
    ;;
  *)
    start_minio
    start_backend
    start_frontend
    sleep 8
    echo "--- 健康检查 ---"
    curl -s --noproxy '*' http://127.0.0.1:5112/api/v1/health && echo ""
    if fe_alive; then echo "前端 5111: OK"; else echo "前端 5111: 启动失败，查 $LOGDIR/frontend.log"; fi
    ;;
esac
