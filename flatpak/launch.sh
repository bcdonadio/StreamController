#!/bin/bash
cd /app/bin/StreamController

if [ -n "$DEBUGPY_PORT" ]; then
  # If DEBUGPY_WAIT=1, wait for the debugger to attach before running
  if [ "$DEBUGPY_WAIT" = "1" ]; then
    echo "DEBUGPY_READY" >&2
    exec python3 -m debugpy --listen 0.0.0.0:${DEBUGPY_PORT} --wait-for-client main.py "$@"
  else
    echo "DEBUGPY_READY" >&2
    exec python3 -m debugpy --listen 0.0.0.0:${DEBUGPY_PORT} main.py "$@"
  fi
else
  exec python3 main.py "$@"
fi
