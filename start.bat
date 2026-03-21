@echo off
chcp 65001 >nul
title 基于大数据的音乐推荐与数据分析系统 - 启动

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║    基于大数据的音乐推荐与数据分析系统                        ║
echo ║    Music Recommendation ^& Data Analysis System               ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

set PROJECT_DIR=%~dp0
set BACKEND_DIR=%PROJECT_DIR%backend
set FRONTEND_DIR=%PROJECT_DIR%frontend
set ADMIN_DIR=%PROJECT_DIR%admin
set SQL_DIR=%PROJECT_DIR%sql
set DB_HOST=localhost
set DB_PORT=3306
set DB_NAME=music_recommend
set DB_USER=root
set DB_PASS=ab123168

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未安装 Python，请先安装
    pause
    exit /b 1
)
echo [OK] Python 已安装

:: 检查 Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未安装 Node.js，请先安装
    pause
    exit /b 1
)
echo [OK] Node.js 已安装

:: 检查 MySQL 并导入数据
mysql -h%DB_HOST% -P%DB_PORT% -u%DB_USER% -p%DB_PASS% -e "USE %DB_NAME%" >nul 2>&1
if errorlevel 1 (
    echo [数据库] 正在导入数据库...
    if exist "%SQL_DIR%\init.sql" (
        mysql -h%DB_HOST% -P%DB_PORT% -u%DB_USER% -p%DB_PASS% --default-character-set=utf8mb4 < "%SQL_DIR%\init.sql"
        echo [OK] 表结构导入完成
    )
    if exist "%SQL_DIR%\data.sql" (
        mysql -h%DB_HOST% -P%DB_PORT% -u%DB_USER% -p%DB_PASS% --default-character-set=utf8mb4 < "%SQL_DIR%\data.sql"
        echo [OK] 测试数据导入完成
    )
) else (
    echo [OK] 数据库已存在
)

:: 安装后端依赖
cd /d "%BACKEND_DIR%"
pip install -r requirements.txt -q 2>nul
echo [OK] Python 依赖已就绪

:: 启动后端（红色窗口）
echo [启动] 启动后端服务...
start "后端-Flask" /min cmd /k "cd /d %BACKEND_DIR% && color 4F && python run.py"

:: 启动前端
if exist "%FRONTEND_DIR%\package.json" (
    if not exist "%FRONTEND_DIR%\node_modules" (
        cd /d "%FRONTEND_DIR%" && pnpm install
    )
    echo [启动] 启动用户端...
    start "前端-Vue" /min cmd /k "cd /d %FRONTEND_DIR% && color 2F && pnpm dev --port 5173"
)

:: 启动管理端
if exist "%ADMIN_DIR%\package.json" (
    if not exist "%ADMIN_DIR%\node_modules" (
        cd /d "%ADMIN_DIR%" && pnpm install
    )
    echo [启动] 启动管理端...
    start "管理端-Admin" /min cmd /k "cd /d %ADMIN_DIR% && color 1F && pnpm dev --port 5174"
)

:: 等待
timeout /t 10 /nobreak >nul

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    服务启动成功！                            ║
echo ╠══════════════════════════════════════════════════════════════╣
echo ║                                                              ║
echo ║  [后端 API]  http://localhost:5000                           ║
echo ║  [用户端]    http://localhost:5173                           ║
echo ║  [管理端]    http://localhost:5174                           ║
echo ║                                                              ║
echo ╠══════════════════════════════════════════════════════════════╣
echo ║  测试账号：                                                  ║
echo ║  管理员: admin / admin123                                    ║
echo ║  运营员: operator / oper123                                  ║
echo ║  用户:   user1 / 123456                                      ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
pause
