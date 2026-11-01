#!/usr/bin/env bash
# Copyright (c) 2026 Albert Wong
# SPDX-License-Identifier: MIT
set -euo pipefail
cd "$(dirname "$0")/.."
docker build -f ../../../docker-images/Dockerfile.python-connector \
  --build-arg CONNECTOR_NAME=source-redis-adbc \
  --build-arg BASE_IMAGE=docker.io/airbyte/python-connector-base:4.1.1@sha256:a268b44c733ae699a60f5fbc06a324945dba98945c6e2ab7f8609f2f895b0d28 \
  -t airbyte/source-redis-adbc:0.1.0 .
