#!/bin/sh
# PostgreSQL 自动备份脚本
# 每天凌晨03:00执行，保留30天

set -e

BACKUP_DIR="/backups"
DB_NAME="${POSTGRES_DB:-starcraft}"
DB_USER="${POSTGRES_USER:-starcraft}"
RETAIN_DAYS=30

# 等待数据库就绪
until pg_isready -h "$PGHOST" -p "$PGPORT" -U "$DB_USER" -d "$DB_NAME"; do
  echo "等待数据库就绪..."
  sleep 5
done

echo "开始备份: $(date)"

# 生成备份文件名
FILENAME="${DB_NAME}_$(date +%Y%m%d_%H%M%S).sql.gz"
FILEPATH="${BACKUP_DIR}/${FILENAME}"

# 执行备份
PGPASSWORD="${POSTGRES_PASSWORD}" pg_dump \
  -h "$PGHOST" \
  -p "$PGPORT" \
  -U "$DB_USER" \
  -d "$DB_NAME" \
  --no-owner \
  --no-privileges | gzip > "$FILEPATH"

echo "备份完成: $FILEPATH"

# 清理过期备份
find "$BACKUP_DIR" -name "${DB_NAME}_*.sql.gz" -mtime +$RETAIN_DAYS -delete
echo "已清理 ${RETAIN_DAYS} 天前的备份"

# 使用循环等待下一次凌晨03:00执行
while true; do
  NEXT_RUN=$(date -d "tomorrow 03:00" +%s 2>/dev/null || date -d "next day 03:00" +%s 2>/dev/null || echo "")
  if [ -z "$NEXT_RUN" ]; then
    # Alpine兼容方式：每24小时执行一次
    sleep 86400
  else
    NOW=$(date +%s)
    SLEEP_SECONDS=$((NEXT_RUN - NOW))
    if [ "$SLEEP_SECONDS" -gt 0 ]; then
      sleep "$SLEEP_SECONDS"
    else
      sleep 86400
    fi
  fi

  echo "开始备份: $(date)"
  FILENAME="${DB_NAME}_$(date +%Y%m%d_%H%M%S).sql.gz"
  FILEPATH="${BACKUP_DIR}/${FILENAME}"

  PGPASSWORD="${POSTGRES_PASSWORD}" pg_dump \
    -h "$PGHOST" \
    -p "$PGPORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    --no-owner \
    --no-privileges | gzip > "$FILEPATH"

  echo "备份完成: $FILEPATH"
  find "$BACKUP_DIR" -name "${DB_NAME}_*.sql.gz" -mtime +$RETAIN_DAYS -delete
  echo "已清理 ${RETAIN_DAYS} 天前的备份"
done
