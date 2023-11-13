#!/usr/bin/env bash

# TODO: This script is only used to provide a temporary but common reporting of connector tests.
# Used test-command.yml 

set -e

. tools/lib/lib.sh


BUCKET=airbyte-connector-build-status

CONNECTOR=$1
RUN_ID=$2
PIPELINE_START_TIMESTAMP=$3
GIT_BRANCH=$4
GIT_REVISION=$5
TEST_OUTCOME=$6
QA_CHECKS_OUTCOME=$7

# Ensure connector is prefixed with connectors/
# TODO (ben): In the future we should just hard error if this is not the case
if [[ $CONNECTOR != *"/"* ]]; then
    CONNECTOR="connectors/$CONNECTOR"
fi
BUCKET_WRITE_ROOT=/tmp/bucket_write_root

CONNECTOR_VERSION=$(get_connector_version "$CONNECTOR")
PREFIX="connectors/"
CONNECTOR_TECHNICAL_NAME=${CONNECTOR#"$PREFIX"}
GITHUB_ACTION_LINK=https://github.com/airbytehq/airbyte/actions/runs/$RUN_ID

export AWS_PAGER=""

function generate_job_log_json() {
  pipeline_end_timestamp="$(date +%s)"
  success=false
  if [ "$TEST_OUTCOME" = "success" ] && [ "$QA_CHECKS_OUTCOME" = "success" ]; then
    success=true
  fi
  pipeline_duration=$(( (pipeline_end_timestamp - PIPELINE_START_TIMESTAMP) ))
  echo "{\"connector_technical_name\": \"$CONNECTOR_TECHNICAL_NAME\", \"connector_version\": \"$CONNECTOR_VERSION\", \"success\": $success,  \"gha_workflow_run_url\": \"$GITHUB_ACTION_LINK\", \"pipeline_start_timestamp\": $PIPELINE_START_TIMESTAMP, \"pipeline_end_timestamp\": $pipeline_end_timestamp, \"pipeline_duration\": $pipeline_duration, \"git_branch\": \"$GIT_BRANCH\", \"git_revision\": \"$GIT_REVISION\", \"ci_context\": \"legacy\"}"
}

function write_report() {
  rm -r $BUCKET_WRITE_ROOT || true
  mkdir -p $BUCKET_WRITE_ROOT
  cd $BUCKET_WRITE_ROOT
  mkdir -p tests/legacy_observability/history/"$CONNECTOR"/"$GIT_BRANCH"/"$DOCKER_VERSION"

  # Generate the JSON for the job log
  local job_log_json=$(generate_job_log_json $timestamp $outcome)
  echo "$job_log_json" > tests/legacy_observability/history/"$CONNECTOR"/"$GIT_BRANCH"/"$DOCKER_VERSION"/"$GIT_REVISION".json

  aws s3 sync "$BUCKET_WRITE_ROOT"/tests/legacy_observability/history/"$CONNECTOR"/"$GIT_BRANCH"/"$DOCKER_VERSION"/ s3://"$BUCKET"/legacy_observability/tests/history/"$CONNECTOR"/"$GIT_BRANCH"/"$DOCKER_VERSION"
}


function main() {
  write_report
}

main
