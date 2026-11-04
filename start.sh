#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "=========================================================="
echo "               Starting Ola AI Code Agent Web UI          "
echo "=========================================================="

# Activate virtualenv if present
if [ -d ".venv" ]; then
    PYTHON_EXEC=".venv/bin/python"
    UVICORN_EXEC=".venv/bin/uvicorn"
else
    PYTHON_EXEC="python3"
    UVICORN_EXEC="uvicorn"
fi

# 1. Start FastAPI backend on port 8000
echo "[Backend] Starting FastAPI on http://localhost:8000..."
$UVICORN_EXEC backend.app:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# 2. Start Next.js frontend on port 3000
echo "[Frontend] Starting Next.js on http://localhost:3000..."
cd "$DIR/frontend"
npm run dev -- -p 3000 &
FRONTEND_PID=$!

# Trap signals to cleanly stop both servers on Ctrl+C
cleanup() {
    echo ""
    echo "[Shutdown] Stopping servers..."
    kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
    wait "$BACKEND_PID" 2>/dev/null || true
    wait "$FRONTEND_PID" 2>/dev/null || true
    echo "[Shutdown] All services stopped."
}

trap cleanup EXIT INT TERM

echo ""
echo "✨ Web UI is ready! Open your browser at:"
echo "👉 http://localhost:3000"
echo ""

wait
