# ── 阶段1: 构建前端 ──
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# ── 阶段2: Nginx托管 ──
FROM nginx:1.27-alpine

LABEL maintainer="starcraft-team"
LABEL description="StarCraft Team Data Platform - Frontend"

# 移除默认配置
RUN rm /etc/nginx/conf.d/default.conf

# 复制Nginx配置
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# 从构建阶段复制产物
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
