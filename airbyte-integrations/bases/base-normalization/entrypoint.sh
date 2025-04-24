#!/usr/bin/env bash

set -e # tells bash, in a script, to exit whenever anything returns a non-zero return value.

function echo2() {
  echo >&2 "$@"
}

function error() {
  echo2 "$@"
  exit 1
}

function config_cleanup() {
  # Remove config file as it might still contain sensitive credentials  (for example,
  # injected OAuth Parameters should not be visible to custom docker images running custom transformation operations)
  rm -f "${CONFIG_FILE}"
}

function check_dbt_event_buffer_size() {
  ret=0
  dbt --help | grep -E -- '--event-buffer-size' && return
  ret=1
}

PROJECT_DIR=$(pwd)

# How many commits should be downloaded from git to view history of a branch
GIT_HISTORY_DEPTH=5

# This function produces a working DBT project folder at the $PROJECT_DIR path so that dbt commands can be run
# from it successfully with the proper credentials. This can be accomplished by providing different custom variables
# to tweak the final project structure. For example, we can either use a user-provided base folder (git repo) or
# use the standard/base template folder to generate normalization models from.
function configuredbt() {
  # We first need to generate a workspace folder for a dbt project to run from:
  if [[ -z "${GIT_REPO}" ]]; then
    # No git repository provided, use the dbt-template folder (shipped inside normalization docker image)
    # as the base folder for dbt workspace
    cp -r /airbyte/normalization_code/dbt-template/* "${PROJECT_DIR}"
    echo "Running: transform-config --config ${CONFIG_FILE} --integration-type ${INTEGRATION_TYPE} --out ${PROJECT_DIR}"
    set +e # allow script to continue running even if next commands fail to run properly
    # Generate a profiles.yml file for the selected destination/integration type
    transform-config --config "${CONFIG_FILE}" --integration-type "${INTEGRATION_TYPE}" --out "${PROJECT_DIR}"
    if [[ -n "${CATALOG_FILE}" ]]; then
      # If catalog file is provided, generate normalization models, otherwise skip it
      echo "Running: transform-catalog --integration-type ${INTEGRATION_TYPE} --profile-config-dir ${PROJECT_DIR} --catalog ${CATALOG_FILE} --out ${PROJECT_DIR}/models/generated/ --json-column _airbyte_data"
      transform-catalog --integration-type "${INTEGRATION_TYPE}" --profile-config-dir "${PROJECT_DIR}" --catalog "${CATALOG_FILE}" --out "${PROJECT_DIR}/models/generated/" --json-column "_airbyte_data"
      TRANSFORM_EXIT_CODE=$?
      if [ ${TRANSFORM_EXIT_CODE} -ne 0 ]; then
        echo -e "\nShowing destination_catalog.json to diagnose/debug errors (${TRANSFORM_EXIT_CODE}):\n"
        cat "${CATALOG_FILE}" | jq
        exit ${TRANSFORM_EXIT_CODE}
      fi
    fi
    set -e # tells bash, in a script, to exit whenever anything returns a non-zero return value.
  else
    trap config_cleanup EXIT
    # Use git repository as a base workspace folder for dbt projects
    if [[ -d git_repo ]]; then
      rm -rf git_repo
    fi
    # Make a shallow clone of the latest git repository in the workspace folder
    if [[ -z "${GIT_BRANCH}" ]]; then
      # Checkout a particular branch from the git repository
      echo "Running: git clone --depth ${GIT_HISTORY_DEPTH} --single-branch  \$GIT_REPO git_repo"
      git clone --depth ${GIT_HISTORY_DEPTH} --single-branch  "${GIT_REPO}" git_repo
    else
      # No git branch specified, use the default branch of the git repository
      echo "Running: git clone --depth ${GIT_HISTORY_DEPTH} -b ${GIT_BRANCH} --single-branch  \$GIT_REPO git_repo"
      git clone --depth ${GIT_HISTORY_DEPTH} -b "${GIT_BRANCH}" --single-branch  "${GIT_REPO}" git_repo
    fi
    # Print few history logs to make it easier for users to verify the right code version has been checked out from git
    echo "Last 5 commits in git_repo:"
    (cd git_repo; git log --oneline -${GIT_HISTORY_DEPTH}; cd -)
    # Generate a profiles.yml file for the selected destination/integration type
    echo "Running: transform-config --config ${CONFIG_FILE} --integration-type ${INTEGRATION_TYPE} --out ${PROJECT_DIR}"
    transform-config --config "${CONFIG_FILE}" --integration-type "${INTEGRATION_TYPE}" --out "${PROJECT_DIR}"
    config_cleanup
  fi
}

## todo: make it easy to select source or destination and validate based on selection by adding an integration type env variable.
function main() {
  CMD="$1"
  shift 1 || error "command not specified."

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
    . /airbyte/sshtunneling.sh
    openssh "${PROJECT_DIR}/ssh.json"
    trap 'closessh' EXIT

    set +e # allow script to continue running even if next commands fail to run properly
    # We don't run dbt 1.0.x on all destinations (because their plugins don't support it yet)
    # So we need to only pass `--event-buffer-size` if it's supported by DBT.
    # Same goes for JSON formatted logging.
    check_dbt_event_buffer_size
    if [ "$ret" -eq 0 ]; then
      echo -e "\nDBT >=1.0.0 detected; using 10K event buffer size\n"
      dbt_additional_args="--event-buffer-size=10000 --log-format json"
    else
      dbt_additional_args=""
    fi

    # Run dbt to compile and execute the generated normalization models
    dbt ${dbt_additional_args} run --profiles-dir "${PROJECT_DIR}" --project-dir "${PROJECT_DIR}"
    DBT_EXIT_CODE=$?
    if [ ${DBT_EXIT_CODE} -ne 0 ]; then
      echo -e "\nDiagnosing dbt debug to check if destination is available for dbt and well configured (${DBT_EXIT_CODE}):\n"
      dbt debug --profiles-dir "${PROJECT_DIR}" --project-dir "${PROJECT_DIR}"
      DBT_DEBUG_EXIT_CODE=$?
      if [ ${DBT_DEBUG_EXIT_CODE} -eq 0 ]; then
        # dbt debug is successful, so the error must be somewhere else...
        echo -e "\nForward dbt output logs to diagnose/debug errors (${DBT_DEBUG_EXIT_CODE}):\n"
        cat "${PROJECT_DIR}/../logs/dbt.log"
      fi
    fi
    closessh
    exit ${DBT_EXIT_CODE}
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
