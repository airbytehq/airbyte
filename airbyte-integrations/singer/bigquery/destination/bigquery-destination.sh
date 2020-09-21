#!/usr/bin/env bash

set -e

case "$1" in
  -c|--config)        CONFIG_FILE="$2"         ;;
  *)                 shift; break             ;;
esac

# Set default_target_schema to the value of dataset_id
PRE_PROCESSED_CONFIG="preprocessed_config.json"
mv "$CONFIG_FILE" "$PRE_PROCESSED_CONFIG"
jq '.default_target_schema = .dataset_id' "$PRE_PROCESSED_CONFIG" > "$CONFIG_FILE"

cat "$CONFIG_FILE" | jq '.credentials_json | fromjson' > credentials.json
GOOGLE_APPLICATION_CREDENTIALS=credentials.json target-bigquery "$@"
