#!/usr/bin/env bash

set -e

case "$1" in
  -c|--config)        CONFIG_FILE="$2"         ;;
  *)                 shift; break             ;;
esac

cat $CONFIG_FILE | jq '.credentials_json | fromjson' > credentials.json
GOOGLE_APPLICATION_CREDENTIALS=credentials.json target-bigquery "$@"
