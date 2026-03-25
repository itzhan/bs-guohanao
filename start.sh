#!/bin/bash
# ============================================================
# 基于大数据的音乐推荐与数据分析系统 - 一键启动脚本 (Mac/Linux)
# ============================================================

set -e

# ============ 配置 ============
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
ADMIN_DIR="$PROJECT_DIR/admin"
SQL_DIR="$PROJECT_DIR/sql"
LOG_DIR="$PROJECT_DIR/.logs"
VENV_DIR="$BACKEND_DIR/.venv"
PYTHON_BIN="/opt/homebrew/opt/python@3.12/bin/python3.12"

DB_HOST="localhost"
DB_PORT="3306"
DB_NAME="music_recommend"
DB_USER="root"
DB_PASS="ab123168"

BACKEND_PORT=5002
FRONTEND_PORT=5179
ADMIN_PORT=5176

# ============ 颜色定义 ============
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m'

# ============ Banner ============
echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}║${NC}    🎵 ${PURPLE}基于大数据的音乐推荐与数据分析系统${NC}                    ${CYAN}║${NC}"
echo -e "${CYAN}║${NC}       Music Recommendation & Data Analysis System            ${CYAN}║${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============ 环境检查 ============
echo -e "${YELLOW}[检查]${NC} 检查基础环境..."

# Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[错误]${NC} 未安装 Python3，请先安装: brew install python3"
    exit 1
fi
echo -e "  ${GREEN}✓${NC} Python3: $(python3 --version 2>&1)"

# pip (will use venv pip, skip system check)

# Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}[错误]${NC} 未安装 Node.js，请先安装: brew install node"
    exit 1
fi
echo -e "  ${GREEN}✓${NC} Node.js: $(node --version)"

# pnpm
if ! command -v pnpm &> /dev/null; then
    echo -e "${YELLOW}[提示]${NC} 正在安装 pnpm..."
    npm install -g pnpm
fi
echo -e "  ${GREEN}✓${NC} pnpm: $(pnpm --version)"

# MySQL
if ! command -v mysql &> /dev/null; then
    echo -e "${RED}[错误]${NC} 未安装 MySQL 客户端，请先安装: brew install mysql"
    exit 1
fi
echo -e "  ${GREEN}✓${NC} MySQL Client: $(mysql --version 2>&1 | head -1)"

echo ""

# ============ MySQL 数据库检查 ============
echo -e "${YELLOW}[数据库]${NC} 检查 MySQL 服务与数据库..."

# 检查 MySQL 服务
if ! mysqladmin ping -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" --silent 2>/dev/null; then
    echo -e "  ${YELLOW}尝试启动 MySQL 服务...${NC}"
    if command -v brew &> /dev/null; then
        brew services start mysql 2>/dev/null || true
    fi
    sleep 3
    if ! mysqladmin ping -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" --silent 2>/dev/null; then
        echo -e "${RED}[错误]${NC} MySQL 服务未运行，请手动启动"
        exit 1
    fi
fi
echo -e "  ${GREEN}✓${NC} MySQL 服务运行中"

# 检查数据库是否存在
DB_EXISTS=$(mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" -e "SHOW DATABASES LIKE '$DB_NAME'" 2>/dev/null | grep "$DB_NAME" || true)
TABLE_COUNT=0
if [ -n "$DB_EXISTS" ]; then
    TABLE_COUNT=$(mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" -N -e "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='$DB_NAME'" 2>/dev/null || echo "0")
fi

if [ -z "$DB_EXISTS" ] || [ "$TABLE_COUNT" -lt 5 ]; then
    echo -e "  ${YELLOW}正在导入数据库...${NC}"
    if [ -f "$SQL_DIR/init.sql" ]; then
        mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" --default-character-set=utf8mb4 < "$SQL_DIR/init.sql" 2>/dev/null
        echo -e "  ${GREEN}✓${NC} 表结构导入完成"
    fi
    if [ -f "$SQL_DIR/data.sql" ]; then
        mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" --default-character-set=utf8mb4 < "$SQL_DIR/data.sql" 2>/dev/null
        echo -e "  ${GREEN}✓${NC} 基础测试数据导入完成"
    fi
    if [ -f "$SQL_DIR/data_expand.sql" ]; then
        mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" --default-character-set=utf8mb4 < "$SQL_DIR/data_expand.sql" 2>/dev/null
        echo -e "  ${GREEN}✓${NC} 扩展数据导入完成"
    fi
    if [ -f "$SQL_DIR/data_10x.sql" ]; then
        mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" --default-character-set=utf8mb4 < "$SQL_DIR/data_10x.sql" 2>/dev/null
        echo -e "  ${GREEN}✓${NC} 10倍扩充数据导入完成"
    fi
else
    echo -e "  ${GREEN}✓${NC} 数据库已存在 ($TABLE_COUNT 张表)"
fi

echo ""

# ============ 安装后端依赖 (使用虚拟环境) ============
echo -e "${YELLOW}[依赖]${NC} 检查后端 Python 依赖..."
if [ -f "$BACKEND_DIR/requirements.txt" ]; then
    cd "$BACKEND_DIR"
    # 创建虚拟环境（如果不存在）
    if [ ! -d "$VENV_DIR" ]; then
        echo -e "  ${YELLOW}创建 Python 虚拟环境...${NC}"
        "$PYTHON_BIN" -m venv "$VENV_DIR"
    fi
    # 激活虚拟环境
    source "$VENV_DIR/bin/activate"
    if ! python3 -c "import flask" 2>/dev/null; then
        echo -e "  ${YELLOW}安装 Python 依赖...${NC}"
        pip install -r requirements.txt -q
    fi
    echo -e "  ${GREEN}✓${NC} Python 依赖已就绪 (venv)"
fi

# ============ 安装前端依赖 ============
if [ -d "$FRONTEND_DIR" ] && [ -f "$FRONTEND_DIR/package.json" ]; then
    echo -e "${YELLOW}[依赖]${NC} 检查前端依赖..."
    if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
        echo -e "  ${YELLOW}安装前端依赖...${NC}"
        cd "$FRONTEND_DIR" && pnpm install
    fi
    echo -e "  ${GREEN}✓${NC} 前端依赖已就绪"
fi

if [ -d "$ADMIN_DIR" ] && [ -f "$ADMIN_DIR/package.json" ]; then
    echo -e "${YELLOW}[依赖]${NC} 检查管理端依赖..."
    if [ ! -d "$ADMIN_DIR/node_modules" ]; then
        echo -e "  ${YELLOW}安装管理端依赖...${NC}"
        cd "$ADMIN_DIR" && pnpm install
    fi
    echo -e "  ${GREEN}✓${NC} 管理端依赖已就绪"
fi

echo ""

# ============ 端口检查 ============
echo -e "${YELLOW}[端口]${NC} 检查端口占用..."
for PORT in $BACKEND_PORT $FRONTEND_PORT $ADMIN_PORT; do
    PID=$(lsof -ti :$PORT 2>/dev/null || true)
    if [ -n "$PID" ]; then
        echo -e "  ${YELLOW}端口 $PORT 被占用 (PID: $PID)，正在释放...${NC}"
        kill -9 $PID 2>/dev/null || true
        sleep 1
    fi
done
echo -e "  ${GREEN}✓${NC} 端口检查完成"

echo ""

# ============ 创建日志目录 ============
mkdir -p "$LOG_DIR"

# ============ 启动后端 ============
echo -e "${YELLOW}[启动]${NC} 启动服务..."

cd "$BACKEND_DIR"
echo -e "  ${BLUE}[后端]${NC} 启动 Flask 后端 (端口: $BACKEND_PORT)..."
"$VENV_DIR/bin/python3" run.py > "$LOG_DIR/backend.log" 2>&1 &
echo $! > "$LOG_DIR/backend.pid"

# ============ 启动前端 ============
if [ -d "$FRONTEND_DIR" ] && [ -f "$FRONTEND_DIR/package.json" ]; then
    cd "$FRONTEND_DIR"
    echo -e "  ${GREEN}[前端]${NC} 启动用户端 (端口: $FRONTEND_PORT)..."
    pnpm dev --port $FRONTEND_PORT > "$LOG_DIR/frontend.log" 2>&1 &
    echo $! > "$LOG_DIR/frontend.pid"
fi

# ============ 启动管理端 ============
if [ -d "$ADMIN_DIR" ] && [ -f "$ADMIN_DIR/package.json" ]; then
    cd "$ADMIN_DIR"
    echo -e "  ${PURPLE}[管理端]${NC} 启动管理端 (端口: $ADMIN_PORT)..."
    pnpm dev --port $ADMIN_PORT > "$LOG_DIR/admin.log" 2>&1 &
    echo $! > "$LOG_DIR/admin.pid"
fi

# ============ 等待就绪 ============
echo ""
echo -e "${YELLOW}[等待]${NC} 等待服务就绪..."
for i in $(seq 1 30); do
    if curl -s http://localhost:$BACKEND_PORT/api/stats/overview > /dev/null 2>&1; then
        break
    fi
    sleep 1
done

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}                    ${GREEN}🎉 服务启动成功！${NC}                       ${CYAN}║${NC}"
echo -e "${CYAN}╠══════════════════════════════════════════════════════════════╣${NC}"
echo -e "${CYAN}║${NC}                                                              ${CYAN}║${NC}"
echo -e "${CYAN}║${NC}  ${BLUE}[后端 API]${NC}  http://localhost:$BACKEND_PORT                    ${CYAN}║${NC}"

if [ -d "$FRONTEND_DIR" ] && [ -f "$FRONTEND_DIR/package.json" ]; then
echo -e "${CYAN}║${NC}  ${GREEN}[用户端]${NC}    http://localhost:$FRONTEND_PORT                    ${CYAN}║${NC}"
fi

if [ -d "$ADMIN_DIR" ] && [ -f "$ADMIN_DIR/package.json" ]; then
echo -e "${CYAN}║${NC}  ${PURPLE}[管理端]${NC}    http://localhost:$ADMIN_PORT                    ${CYAN}║${NC}"
fi

echo -e "${CYAN}║${NC}                                                              ${CYAN}║${NC}"
echo -e "${CYAN}╠══════════════════════════════════════════════════════════════╣${NC}"
echo -e "${CYAN}║${NC}  ${YELLOW}测试账号：${NC}                                                  ${CYAN}║${NC}"
echo -e "${CYAN}║${NC}  ┌──────────┬────────────┬───────────┐                   ${CYAN}║${NC}"
echo -e "${CYAN}║${NC}  │ 角色     │ 用户名     │ 密码      │                   ${CYAN}║${NC}"
echo -e "${CYAN}║${NC}  ├──────────┼────────────┼───────────┤                   ${CYAN}║${NC}"
echo -e "${CYAN}║${NC}  │ 管理员   │ admin      │ admin123  │                   ${CYAN}║${NC}"
echo -e "${CYAN}║${NC}  │ 运营     │ operator   │ oper123   │                   ${CYAN}║${NC}"
echo -e "${CYAN}║${NC}  │ 用户     │ user1      │ 123456    │                   ${CYAN}║${NC}"
echo -e "${CYAN}║${NC}  └──────────┴────────────┴───────────┘                   ${CYAN}║${NC}"
echo -e "${CYAN}║${NC}                                                              ${CYAN}║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}[日志]${NC} 按 Ctrl+C 停止所有服务"
echo ""

# ============ 实时日志输出 ============
cleanup() {
    echo ""
    echo -e "${YELLOW}[停止]${NC} 正在停止所有服务..."
    bash "$PROJECT_DIR/stop.sh" 2>/dev/null || true
    exit 0
}
trap cleanup INT TERM

# 彩色前缀实时输出日志
tail -f "$LOG_DIR/backend.log" 2>/dev/null | sed "s/^/$(printf "${BLUE}[后端] ${NC}")/" &
TAIL_PIDS=$!

if [ -f "$LOG_DIR/frontend.log" ]; then
    tail -f "$LOG_DIR/frontend.log" 2>/dev/null | sed "s/^/$(printf "${GREEN}[前端] ${NC}")/" &
    TAIL_PIDS="$TAIL_PIDS $!"
fi

if [ -f "$LOG_DIR/admin.log" ]; then
    tail -f "$LOG_DIR/admin.log" 2>/dev/null | sed "s/^/$(printf "${PURPLE}[管理] ${NC}")/" &
    TAIL_PIDS="$TAIL_PIDS $!"
fi

wait
