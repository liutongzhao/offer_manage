#!/bin/zsh
# 数据备份脚本：SQLite 数据库 + MinIO 全部对象
# 用法：zsh backup.sh [备份目录]     （服务器上建议挂 crontab 每日一跑）
# 恢复：见 docs/05-部署/部署指南.md「数据备份与恢复」一节

set -e
cd "$(dirname "$0")"

# 读 compose 用的凭据（优先同目录 backend.env，服务器实际在 /opt/offer/backend.env）
[ -f backend.env ] && source backend.env || true
[ -f /opt/offer/backend.env ] && source /opt/offer/backend.env || true

BACKUP_DIR="${1:-./backups}"
STAMP=$(date +%Y%m%d-%H%M%S)
mkdir -p "$BACKUP_DIR/$STAMP"

# 1. SQLite：用 backup 命令保证一致性（不能直接 cp 正在写的库）
docker exec offer-backend python -c "
import sqlite3
src = sqlite3.connect('/app/data/app.db')
dst = sqlite3.connect('/tmp/app-backup.db')
src.backup(dst)
dst.close(); src.close()
" && docker cp offer-backend:/tmp/app-backup.db "$BACKUP_DIR/$STAMP/app.db"
docker exec offer-backend rm -f /tmp/app-backup.db

# 2. MinIO：mc 镜像整个桶（网络名从 backend 容器动态取）
NET=$(docker inspect offer-backend --format '{{range $k,$_ := .NetworkSettings.Networks}}{{$k}}{{end}}')
docker run --rm --network "$NET" \
  -v "$(cd "$BACKUP_DIR/$STAMP" && pwd):/backup" \
  --entrypoint /bin/sh minio/mc -c "
mc alias set local http://minio:9000 '$MINIO_ROOT_USER' '$MINIO_ROOT_PASSWORD' >/dev/null &&
mc mirror --overwrite local/qiuzhao /backup/minio/
"

echo "备份完成：$BACKUP_DIR/$STAMP（app.db + minio/）"
