#!/usr/bin/env bash

set -e

function echo2() {
  echo >&2 "$@"
}

function error() {
  echo2 "$@"
  exit 1
}

PROJECT_DIR=$(pwd)

## todo: make it easy to select source or destination and validate based on selection by adding an integration type env variable.
function main() {
  CMD="$1"
  shift 1 || error "command not specified."

  ARGS=
  while [ $# -ne 0 ]; do
    case "$1" in
    --config)
      CONFIG_FILE="$2"
      shift 2
      ;;
    --catalog)
      CATALOG_FILE="$2"
      shift 2
      ;;
    --integration-type)
      INTEGRATION_TYPE="$2"
      shift 2
      ;;
    *)
      error "Unknown option: $1"
      ;;
    esac
  done

  case "$CMD" in
  run)
    cp -r /airbyte/normalization_code/dbt-template/* $PROJECT_DIR
    transform-config --config "$CONFIG_FILE" --integration-type "$INTEGRATION_TYPE" --out $PROJECT_DIR
    transform-catalog --integration-type "$INTEGRATION_TYPE" --profile-config-dir $PROJECT_DIR --catalog "$CATALOG_FILE" --out $PROJECT_DIR/models/generated/ --json-column _airbyte_data
    dbt run --profiles-dir $PROJECT_DIR --project-dir $PROJECT_DIR
    ;;
  dry-run)
    cp -r /airbyte/normalization_code/dbt-template/* $PROJECT_DIR
    transform-config --config "$CONFIG_FILE" --integration-type "$INTEGRATION_TYPE" --out $PROJECT_DIR
    dbt debug --profiles-dir $PROJECT_DIR --project-dir $PROJECT_DIR
    transform-catalog --profile-config-dir $PROJECT_DIR --catalog "$CATALOG_FILE" --out $PROJECT_DIR/models/generated/ --json-column _airbyte_data
    dbt compile --profiles-dir $PROJECT_DIR --project-dir $PROJECT_DIR
    ;;
  *)
    error "Unknown command: $CMD"
    ;;
  esac
}

main "$@"
