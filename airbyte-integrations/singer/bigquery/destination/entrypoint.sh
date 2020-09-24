#!/usr/bin/env bash

set -e

function echo2() {
  echo >&2 "$@"
}

function error() {
  echo2 "$@"
  exit 1
}

function main() {
  ARGS=
  CONFIG_FILE=
  while [ $# -ne 0 ]; do
    case "$1" in
    --discover)
      DISCOVER=1
      shift 1
      break
      ;;
    --config)
      CONFIG_FILE=$2
      ARGS="$ARGS --config $CONFIG_FILE"
      shift 2
      ;;
    --state)
      # ignore
      shift 2
      ;;
    --properties)
      # ignore
      shift 2
      ;;
    *)
      error "Unknown option: $1"
      ;;
    esac
  done


  # Set default_target_schema to the value of dataset_id
  ORIGINAL_CONFIG_FILE="original_config.json"
  mv "$CONFIG_FILE" "$ORIGINAL_CONFIG_FILE"
  jq '.default_target_schema = .dataset_id' "$ORIGINAL_CONFIG_FILE" > "$CONFIG_FILE"

  # Extract credentials
  cat "$CONFIG_FILE" | jq '.credentials_json | fromjson' > credentials.json

  # Singer's discovery is what we currently use to check connection
  if [ "$DISCOVER" == 1 ]; then
    echo2 "Checking connection..."
    gcloud auth activate-service-account --key-file credentials.json 1>&2
    bq ls 1>&2 || error "Invalid credentials"
    echo '{"streams":[]}'
  else
    GOOGLE_APPLICATION_CREDENTIALS=credentials.json target-bigquery $ARGS
  fi
}

main "$@"
