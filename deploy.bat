@echo off
chcp 65001 >nul
title 音乐推荐系统 - Docker 启动

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║    基于大数据的音乐推荐与数据分析系统 - Docker 部署          ║
echo ║    Music Recommendation ^& Data Analysis System               ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: 检查 Docker 是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Docker，请先安装 Docker Desktop
    echo        下载地址: https://www.docker.com/products/docker-desktop/
    echo.
    pause
    exit /b 1
)
echo [OK] Docker 已安装: 
docker --version

:: 检查 Docker 是否运行
docker info >nul 2>&1
if errorlevel 1 (
    echo [错误] Docker Desktop 未启动，请先启动 Docker Desktop
    echo        启动后等待右下角 Docker 图标显示 "Docker Desktop is running"
    echo.
    pause
    exit /b 1
)
echo [OK] Docker 服务运行中

echo.
echo [启动] 正在启动所有服务...
echo.

:: 直接启动（不构建）
docker compose up -d

if errorlevel 1 (
    echo.
    echo [错误] 启动失败，请检查错误信息
    echo        如果是首次部署，请先运行: docker compose up --build -d
    pause
    exit /b 1
)

:: 等待后端就绪
echo.
echo [等待] 等待服务就绪（数据库初始化中）...
timeout /t 20 /nobreak >nul

:: 检查服务状态
echo.
echo [状态] 服务运行状态:
docker compose ps

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    启动成功！                                ║
echo ╠══════════════════════════════════════════════════════════════╣
echo ║                                                              ║
echo ║  [用户端]    http://localhost:5179                           ║
echo ║  [管理端]    http://localhost:5176                           ║
echo ║  [后端 API]  http://localhost:5002                           ║
echo ║                                                              ║
echo ╠══════════════════════════════════════════════════════════════╣
echo ║  测试账号：                                                  ║
echo ║  ┌──────────┬────────────┬───────────┐                      ║
echo ║  │ 角色     │ 用户名     │ 密码      │                      ║
echo ║  ├──────────┼────────────┼───────────┤                      ║
echo ║  │ 管理员   │ admin      │ admin123  │                      ║
echo ║  │ 运营员   │ operator   │ oper123   │                      ║
echo ║  │ 用户     │ user1      │ 123456    │                      ║
echo ║  └──────────┴────────────┴───────────┘                      ║
echo ╠══════════════════════════════════════════════════════════════╣
echo ║                                                              ║
echo ║  停止服务: 运行 stop-docker.bat                              ║
echo ║  查看日志: docker compose logs -f                            ║
echo ║  重新构建: docker compose up --build -d                      ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
pause
