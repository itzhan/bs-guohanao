@echo off
chcp 65001 >nul
echo [停止] 正在停止所有 Docker 服务...
docker compose down
echo [完成] 所有服务已停止
echo.
echo 如需清除数据（重新导入数据库），请运行:
echo   docker compose down -v
echo.
pause
