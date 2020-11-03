#!/usr/bin/env bash

TRANSFORMED_CONFIG=transformed_config.json
DBT_MODEL=dbt_model.json
set -e

function echo2() {
  echo >&2 "$@"
}

function error() {
  echo2 "$@"
  exit 1
}

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
    transform-config --config "$CONFIG_FILE" --integration-type "$INTEGRATION_TYPE" --out "$TRANSFORMED_CONFIG"
#    transform-catalog --catalog "$CATALOG_FILE" --out "$DBT_MODEL"
    cat $TRANSFORMED_CONFIG
#    cat $DBT_MODEL
#    execute-dbt --config "$TRANSFORMED_CONFIG" --model "$DBT_MODEL"
    ;;
  dry-run)
    error "Not Implemented"
    ;;
  *)
    error "Unknown command: $CMD"
    ;;
  esac
}

main "$@"
