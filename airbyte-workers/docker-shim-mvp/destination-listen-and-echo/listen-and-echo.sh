#!/usr/bin/env bash

socat -d -d -d TCP-LISTEN:"${DEST_PORT}",bind="${DEST_IP}" stdout
