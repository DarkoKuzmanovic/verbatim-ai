#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

# Load environment
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Activate virtual environment
source venv/bin/activate

# Start application
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8001}"
