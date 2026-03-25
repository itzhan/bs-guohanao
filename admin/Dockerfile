# ---- 构建阶段 ----
FROM node:20-alpine AS builder
RUN corepack enable && corepack prepare pnpm@latest --activate
WORKDIR /app
COPY package.json pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile || pnpm install
COPY . .
RUN pnpm build

# ---- 运行阶段 ----
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html/admin
COPY nginx-admin.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
