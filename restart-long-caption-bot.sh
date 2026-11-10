#!/bin/bash
set -euo pipefail

# this script restarts long caption bot
# it closes the processes from before and starts it again

SCRIPT_NAME="long_caption_bot.py"
SCRIPT_DIR=$(dirname "$(realpath "$0")")
cd "$SCRIPT_DIR"

# private-router must be up (owns Telethon)
if ! curl -sf http://127.0.0.1:3010/health >/dev/null; then
    echo "private-router is down — starting it first..."
    /root/Storage/private-router/restart.sh
    sleep 2
fi

echo "Finding and killing the old process..."
PIDS=$(pgrep -f "$SCRIPT_NAME" || true)
if [ -n "${PIDS}" ]; then
    echo "Killing process(es): $PIDS"
    # shellcheck disable=SC2086
    kill -9 $PIDS || true
else
    echo "No running process found."
fi

# shellcheck disable=SC1091
set -a
if [ -f /root/Storage/private-router/.env ]; then
    # shellcheck disable=SC1091
    . /root/Storage/private-router/.env
fi
set +a

# activate virtual environment
# shellcheck disable=SC1091
source "$SCRIPT_DIR/venv/bin/activate"
"$SCRIPT_DIR/venv/bin/pip" install -q -r "$SCRIPT_DIR/requirements.txt"

nohup python3 "$SCRIPT_NAME" > /dev/null 2>&1 &
echo "long-caption-bot started"
