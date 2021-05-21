#!/usr/bin/env bash

echo "ip: ${SRC_IP}", "port: ${SRC_PORT}"
echo "$@"
python "/airbyte/integration_code/main.py" "$@" | socat -d -d -d - TCP:${SRC_IP}:${SRC_PORT}
