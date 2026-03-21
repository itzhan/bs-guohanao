@echo off
chcp 65001 >nul
echo [停止] 正在停止所有服务...

:: 停止后端
taskkill /FI "WINDOWTITLE eq 后端-Flask*" /F >nul 2>&1
:: 停止前端
taskkill /FI "WINDOWTITLE eq 前端-Vue*" /F >nul 2>&1
:: 停止管理端
taskkill /FI "WINDOWTITLE eq 管理端-Admin*" /F >nul 2>&1

:: 通过端口清理
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5000 " ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5173 " ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5174 " ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1

echo [完成] 所有服务已停止
pause
