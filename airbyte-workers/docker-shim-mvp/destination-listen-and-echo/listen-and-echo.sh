#!/usr/bin/env bash

echo "ip: ${DEST_IP}", "port: ${DEST_PORT}"
socat -d -d -d TCP-LISTEN:"${DEST_PORT}",bind="${DEST_IP}" stdout
