#!/bin/bash
# ============================================================
# 基于大数据的音乐推荐与数据分析系统 - 一键停止脚本 (Mac/Linux)
# ============================================================

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$PROJECT_DIR/.logs"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}[停止]${NC} 正在停止所有服务..."

# 通过 PID 文件停止
for SERVICE in backend frontend admin; do
    PID_FILE="$LOG_DIR/$SERVICE.pid"
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID" 2>/dev/null
            echo -e "  ${GREEN}✓${NC} 停止 $SERVICE (PID: $PID)"
        fi
        rm -f "$PID_FILE"
    fi
done

# 通过端口停止（双重清理）
for PORT in 5001 5173 5174; do
    PID=$(lsof -ti :$PORT 2>/dev/null || true)
    if [ -n "$PID" ]; then
        kill -9 $PID 2>/dev/null || true
        echo -e "  ${GREEN}✓${NC} 清理端口 $PORT (PID: $PID)"
    fi
done

# 清理 tail 监控进程
pkill -f "tail -f $LOG_DIR" 2>/dev/null || true

echo -e "${GREEN}[完成]${NC} 所有服务已停止"
