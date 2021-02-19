#!/usr/bin/env bash

set -e

LOCAL_RESTISH_PATH="$(pwd)"/airbyte-cli/restish.json
IMAGE_RESTISH_PATH=/root/.restish/apis.json

DOWNLOADED_CONFIG_PATH=/tmp/downloaded-airbyte-api-config
IMAGE_CONFIG_PATH=/tmp/config.yaml

API_URL=http://localhost:8001
curl -s "$API_URL"/api/v1/openapi -o "$DOWNLOADED_CONFIG_PATH"

cat > "$LOCAL_RESTISH_PATH" <<EOL
{
  "airbyte": {
    "base": "${API_URL}",
    "spec_files": ["${IMAGE_CONFIG_PATH}"]
  }
}
EOL

docker run --rm \
  -v "$LOCAL_RESTISH_PATH":"$IMAGE_RESTISH_PATH" \
  -v "$DOWNLOADED_CONFIG_PATH":"$IMAGE_CONFIG_PATH"  \
  --network host \
  airbyte/cli:0.1.0 \
  airbyte \
  $@
