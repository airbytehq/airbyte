#!/usr/bin/env bash

echo "$@"
python "/airbyte/integration_code/main.py" "$@" | socat -d -d -d - TCP:host.docker.internal:9000
