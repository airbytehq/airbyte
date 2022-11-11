#!/usr/bin/env bash

set -e

LOCAL_RESTISH_PATH="$(pwd)"/airbyte-cli/restish.json
IMAGE_RESTISH_PATH=/root/.restish/apis.json

DOWNLOADED_CONFIG_PATH=/tmp/downloaded-airbyte-api-config
IMAGE_CONFIG_PATH=/tmp/config.yaml

if [ ! -f "$LOCAL_RESTISH_PATH" ]; then
  API_URL="${API_URL:-http://localhost:8001}"
  if ! curl -s "${API_URL}/api/v1/openapi" -o "$DOWNLOADED_CONFIG_PATH"; then
    2>&1 echo "ERROR: failed to download config file from ${API_URL}/api/v1/openapi"
    2>&1 echo "       if the API is elsewhere you can specify it using:"
    2>&1 echo "       API_URL=XXX $0"
    exit 1
  fi

  cat > "$LOCAL_RESTISH_PATH" <<EOL
{
  "airbyte": {
    "base": "${API_URL}",
    "spec_files": ["${IMAGE_CONFIG_PATH}"]
  }
}
EOL
else
  echo "using config file: $LOCAL_RESTISH_PATH"
fi

docker run --rm \
  -v "$LOCAL_RESTISH_PATH":"$IMAGE_RESTISH_PATH" \
  -v "$DOWNLOADED_CONFIG_PATH":"$IMAGE_CONFIG_PATH"  \
  --network host \
  airbyte/cli:0.1.0 \
  airbyte \
  $@
