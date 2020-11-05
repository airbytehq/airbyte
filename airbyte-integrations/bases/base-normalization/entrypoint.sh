#!/usr/bin/env bash

set -e

# dbt looks specifically for files named profiles.yml and dbt_project.yml
DBT_PROFILE=profiles.yml
DBT_MODEL=dbt_project.yml

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
    transform-config --config "$CONFIG_FILE" --integration-type "$INTEGRATION_TYPE" --out "$DBT_PROFILE"
    transform-catalog --catalog "$CATALOG_FILE" --out "$DBT_MODEL" --json-column data --table "???"
    dbt deps --profiles-dir $(pwd) --project-dir $(pwd)
    dbt run --profiles-dir $(pwd) --project-dir $(pwd)
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
