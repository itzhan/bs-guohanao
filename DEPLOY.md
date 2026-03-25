# 🎵 基于大数据的音乐推荐与数据分析系统 — 部署指南

## 一、环境要求

客户电脑只需安装一个软件：

| 软件 | 下载地址 |
|------|----------|
| **Docker Desktop** | https://www.docker.com/products/docker-desktop/ |

> 安装完成后重启电脑，启动 Docker Desktop，等待右下角托盘图标显示绿色 "Running" 状态。

---

## 二、一键部署（推荐）

### 步骤

1. 将整个项目文件夹拷贝到客户电脑（U盘 / 网盘均可）
2. 双击运行 `deploy.bat`
3. 首次部署需 5-10 分钟（下载镜像 + 构建），请耐心等待
4. 看到 "部署成功" 提示后，打开浏览器访问：

| 服务 | 地址 |
|------|------|
| 用户端 | http://localhost:5173 |
| 管理端 | http://localhost:5174 |
| 后端 API | http://localhost:5001 |

### 测试账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 运营员 | operator | oper123 |
| 用户 | user1 | 123456 |

---

## 三、常用操作

```bash
# 停止服务
双击 stop-docker.bat

# 或在命令行中：
docker compose down

# 查看实时日志
docker compose logs -f

# 查看某个服务日志
docker compose logs -f backend

# 重新部署（保留数据）
docker compose up --build -d

# 重新部署（清除所有数据，重新导入）
docker compose down -v
docker compose up --build -d
```

---

## 四、常见问题

### Q: 端口被占用怎么办？
修改 `docker-compose.yml` 中 `ports` 映射的左侧端口号，例如将 `5173:80` 改为 `8080:80`。

### Q: 首次启动后端报数据库连接错误？
这通常是 MySQL 尚未初始化完成，等待 30 秒后刷新页面即可。

### Q: 如何完全重置？
运行 `docker compose down -v` 会删除所有数据卷（包括数据库），然后重新 `docker compose up --build -d`。
