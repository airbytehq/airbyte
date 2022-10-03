#!/bin/bash
while True; do
    echo "Check if server connection still alive..."

    if curl -sSf -o /dev/null http://localhost:8001/api/v1/health; then
        echo "Connection is alive..."
    else
        echo "Connection is not alive..."
        echo "Port forwarding pod..."
        kubectl port-forward svc/airbyte-server-svc 8001:8001 &
    fi
    sleep 5
done