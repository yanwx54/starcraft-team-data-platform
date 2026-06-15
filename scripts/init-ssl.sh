#!/bin/bash
# SSL证书初始化脚本
# 使用Let's Encrypt获取免费SSL证书
#
# 使用方法：
#   1. 修改 DOMAIN 为你的域名
#   2. 修改 EMAIL 为你的邮箱
#   3. 执行: bash scripts/init-ssl.sh

set -e

DOMAIN="${1:?请提供域名，例如: bash scripts/init-ssl.sh example.com}"
EMAIL="${2:?请提供邮箱，例如: bash scripts/init-ssl.sh example.com user@example.com}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SSL_DIR="${PROJECT_DIR}/nginx/ssl"
CERTBOT_WEBROOT="${PROJECT_DIR}/nginx/certbot-webroot"

echo "=== 初始化SSL证书 ==="
echo "域名: $DOMAIN"
echo "邮箱: $EMAIL"

# 创建必要目录
mkdir -p "$SSL_DIR"
mkdir -p "$CERTBOT_WEBROOT"

# 检查是否已有证书
if [ -f "$SSL_DIR/fullchain.pem" ]; then
  echo "检测到已有证书，跳过初始化"
  echo "如需更新，请运行: docker compose run --rm certbot renew"
  exit 0
fi

# 使用自签名证书作为初始证书（让Nginx能启动）
echo "生成自签名证书（临时）..."
openssl req -x509 -nodes \
  -newkey rsa:2048 \
  -days 1 \
  -keyout "$SSL_DIR/privkey.pem" \
  -out "$SSL_DIR/fullchain.pem" \
  -subj "/CN=${DOMAIN}"

echo "自签名证书已生成"
echo ""
echo "=== 下一步 ==="
echo "1. 启动服务: docker compose up -d starcraft-web"
echo "2. 获取正式证书: docker compose run --rm certbot certonly --webroot -w /var/www/certbot -d ${DOMAIN} --email ${EMAIL} --agree-tos --no-eff-email"
echo "3. 复制正式证书到 nginx/ssl/"
echo "4. 重启Nginx: docker compose restart starcraft-web"
