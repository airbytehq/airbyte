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

function configuredbt() {
  if [[ -z "${GIT_REPO}" ]]; then
    cp -r /airbyte/normalization_code/dbt-template/* "${PROJECT_DIR}"
    echo "Running: transform-config --config ${CONFIG_FILE} --integration-type ${INTEGRATION_TYPE} --out ${PROJECT_DIR}"
    transform-config --config "${CONFIG_FILE}" --integration-type "${INTEGRATION_TYPE}" --out "${PROJECT_DIR}"
    if [[ ! -z "${CATALOG_FILE}" ]]; then
      echo "Running: transform-catalog --integration-type ${INTEGRATION_TYPE} --profile-config-dir ${PROJECT_DIR} --catalog ${CATALOG_FILE} --out ${PROJECT_DIR}/models/generated/ --json-column _airbyte_data"
      transform-catalog --integration-type "${INTEGRATION_TYPE}" --profile-config-dir "${PROJECT_DIR}" --catalog "${CATALOG_FILE}" --out "${PROJECT_DIR}/models/generated/" --json-column "_airbyte_data"
    fi
  else
    if [[ -z "${GIT_BRANCH}" ]]; then
      echo "Running: git clone --depth 1 --single-branch  \$GIT_REPO git_repo"
      git clone --depth 1 --single-branch  "${GIT_REPO}" git_repo
    else
      echo "Running: git clone --depth 1 -b ${GIT_BRANCH} --single-branch  \$GIT_REPO git_repo"
      git clone --depth 1 -b "${GIT_BRANCH}" --single-branch  "${GIT_REPO}" git_repo
    fi
    echo "Running: transform-config --config ${CONFIG_FILE} --integration-type ${INTEGRATION_TYPE} --out ${PROJECT_DIR}"
    transform-config --config "${CONFIG_FILE}" --integration-type "${INTEGRATION_TYPE}" --out "${PROJECT_DIR}"
  fi
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
    --git-repo)
      GIT_REPO="$2"
      shift 2
      ;;
    --git-branch)
      GIT_BRANCH="$2"
      shift 2
      ;;
    *)
      error "Unknown option: $1"
      ;;
    esac
  done

  case "$CMD" in
  run)
    configuredbt
    dbt run --profiles-dir "${PROJECT_DIR}" --project-dir "${PROJECT_DIR}"
    ;;
  configure-dbt)
    configuredbt
    ;;
  *)
    error "Unknown command: $CMD"
    ;;
  esac
}

main "$@"
