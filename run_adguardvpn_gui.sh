#!/usr/bin/env bash
# Launcher script for AdGuard VPN GUI
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -x "$DIR/.venv/bin/python" ]; then
  PY="$DIR/.venv/bin/python"
else
  PY="$(command -v python3 || command -v python || true)"
fi

if [ -z "$PY" ]; then
  echo "Python not found. Install Python 3 and try again."
  exit 1
fi

exec "$PY" "$DIR/main.py" "$@"
