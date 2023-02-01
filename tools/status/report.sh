#!/usr/bin/env bash

set -e

. tools/lib/lib.sh


BUCKET=airbyte-connector-build-status

CONNECTOR=$1
REPOSITORY=$2
RUN_ID=$3
TEST_OUTCOME=$4

# TODO: Disabled for on master until #22127 resolved
# QA_CHECKS_OUTCOME=$5
QA_CHECKS_OUTCOME=success

# Ensure connector is prefixed with connectors/
# TODO (ben): In the future we should just hard error if this is not the case
if [[ $CONNECTOR != *"/"* ]]; then
    CONNECTOR="connectors/$CONNECTOR"
fi

BUCKET_WRITE_ROOT=/tmp/bucket_write_root
LAST_TEN_ROOT=/tmp/last_ten_root
SUMMARY_WRITE_ROOT=/tmp/summary_write_root
VERSION_PREFIX="version-"

DOCKER_VERSION=$(get_connector_version "$CONNECTOR")

GITHUB_ACTION_LINK=https://github.com/$REPOSITORY/actions/runs/$RUN_ID

export AWS_PAGER=""

function generate_job_log_json() {
  local timestamp=$1
  local outcome=$2

  echo "{ \"link\": \"$GITHUB_ACTION_LINK\", \"outcome\": \"$outcome\", \"docker_version\": \"$DOCKER_VERSION\", \"timestamp\": \"$timestamp\", \"connector\": \"$CONNECTOR\" }"
}

function write_job_log() {
  rm -r $BUCKET_WRITE_ROOT || true
  mkdir -p $BUCKET_WRITE_ROOT
  cd $BUCKET_WRITE_ROOT
  mkdir -p tests/history/"$CONNECTOR"/"$DOCKER_VERSION"

  local timestamp="$(date +%s)"
  local outcome=failure
  if [ "$TEST_OUTCOME" = "success" ] && [ "$QA_CHECKS_OUTCOME" = "success" ]; then
    outcome=success
  fi

  # Generate the JSON for the job log
  local job_log_json=$(generate_job_log_json "$timestamp" "$outcome")
  echo "$job_log_json" > tests/history/"$CONNECTOR"/"$timestamp".json

  # if docker version has a value, write it to a file with the docker version as the name
  # else output an error to the build log
  if [ -n "$DOCKER_VERSION" ]; then
    echo "$job_log_json" > tests/history/"$CONNECTOR"/"$VERSION_PREFIX""$DOCKER_VERSION".json
  else
    echo "ERROR: Could not find docker version for $CONNECTOR"
  fi

  aws s3 sync "$BUCKET_WRITE_ROOT"/tests/history/"$CONNECTOR"/ s3://"$BUCKET"/tests/history/"$CONNECTOR"/
}

function pull_latest_job_logs() {
  # pull the logs for the latest ten jobs for this connector
  # note this is done by key as each log has a timestamp in the filename
  # ensuring that the version specific runs are filtered out.
  LAST_TEN_FILES=$(aws s3api list-objects-v2 --bucket "$BUCKET"  \
    --prefix "tests/history/$CONNECTOR" \
    --query "reverse(sort_by(Contents[?!contains(Key, \`$VERSION_PREFIX\`)], &Key))[:10].Key" \
    --output=text)

  rm -r $LAST_TEN_ROOT || true
  mkdir -p $LAST_TEN_ROOT

  for file in $LAST_TEN_FILES; do
    aws s3 cp s3://"$BUCKET"/"$file" $LAST_TEN_ROOT/
  done
}

function write_badge_and_summary() {
  HTML_TABLE_ROWS=""

  successes=0
  failures=0

  while IFS= read -r file; do
    line=$(cat "$LAST_TEN_ROOT/$file")
    outcome=$(echo "$line" | jq -r '.outcome')
    if [ "$outcome" = "success" ]; then
      successes=$((successes+1))
      outcome_output="<span style=\"color:green;\">&#10004; $outcome</span>"
    else
      failures=$((failures+1))
      outcome_output="<span style=\"color:red;\">&#10008; $outcome</span>"
    fi
    link=$(echo "$line" | jq -r '.link')
    date_string=$(echo "$file" | cut -f 1 -d '.')

    # Mac uses a different way to render datetime strings with "date"
    uname_output="$(uname -s)"
    case "${uname_output}" in
        Darwin*)    rendered_date=$(date -r "$date_string");;
        *)          rendered_date=$(date -d @"$date_string")
    esac
    HTML_TABLE_ROWS="<tr><td>$rendered_date</td><td>$outcome_output</td><td><a href=\"$link\">$link</a></td></tr>$HTML_TABLE_ROWS"
  done <<< "$(ls $LAST_TEN_ROOT)"

  echo "successes: $successes"
  echo "failures: $failures"

  if [ "$failures" = "0" ]; then
    color="green"
    message="✔ $successes"
  elif [ "$(cat $LAST_TEN_ROOT/* | tail -n1 | jq -r ".outcome")" = "success" ]; then
    color="yellow"
    message="✔ $successes | ✘ $failures"
  elif [ "$successes" = "0" ]; then
    color="red"
    message="✘ $failures"
  else
    color="red"
    message="✔ $successes | ✘ $failures"
  fi

  echo "color: $color"
  echo "message: $message"

  HTML_TOP="<html><head><title>$CONNECTOR</title><style>body {padding:20px; font-family:monospace;} table {border-collapse: collapse;} th, td {padding:20px; text-align:left;} th, td { border:1px solid #c5c4ff;} </style></head><body><p><img src=\"https://img.shields.io/endpoint?url=https%3A%2F%2Fairbyte-connector-build-status.s3-website.us-east-2.amazonaws.com%2Ftests%2Fsummary%2F$CONNECTOR%2Fbadge.json\"></p><h1>$CONNECTOR</h1>"
  HTML_BOTTOM="</body></html>"
  HTML_TABLE="<table><tr><th>datetime</th><th>status</th><th>workflow</th></tr>$HTML_TABLE_ROWS</table>"

  HTML="$HTML_TOP $HTML_TABLE $HTML_BOTTOM"
  BADGE="{ \"schemaVersion\": 1, \"label\": \"\", \"labelColor\": \"#c5c4ff\", \"message\": \"$message\", \"color\": \"$color\", \"cacheSeconds\": 300, \"logoSvg\": \"<svg version=\\\"1.0\\\" xmlns=\\\"http://www.w3.org/2000/svg\\\"\\n width=\\\"32.000000pt\\\" height=\\\"32.000000pt\\\" viewBox=\\\"0 0 32.000000 32.000000\\\"\\n preserveAspectRatio=\\\"xMidYMid meet\\\">\\n\\n<g transform=\\\"translate(0.000000,32.000000) scale(0.100000,-0.100000)\\\"\\nfill=\\\"#000000\\\" stroke=\\\"none\\\">\\n<path d=\\\"M136 279 c-28 -22 -111 -157 -102 -166 8 -8 34 16 41 38 8 23 21 25\\n29 3 3 -8 -6 -35 -20 -60 -18 -31 -22 -44 -12 -44 20 0 72 90 59 103 -6 6 -11\\n27 -11 47 0 77 89 103 137 41 18 -23 16 -62 -5 -96 -66 -109 -74 -125 -59\\n-125 24 0 97 140 97 185 0 78 -92 123 -154 74z\\\"/>\\n<path d=\\\"M168 219 c-22 -13 -23 -37 -2 -61 12 -12 14 -22 7 -30 -5 -7 -22 -34\\n-37 -60 -20 -36 -23 -48 -12 -48 13 0 106 147 106 169 0 11 -28 41 -38 41 -4\\n0 -15 -5 -24 -11z m32 -34 c0 -8 -4 -15 -10 -15 -5 0 -10 7 -10 15 0 8 5 15\\n10 15 6 0 10 -7 10 -15z\\\"/>\\n</g>\\n</svg>\\n\" }"

  rm -r $SUMMARY_WRITE_ROOT || true
  mkdir -p $SUMMARY_WRITE_ROOT/tests/summary/"$CONNECTOR"

  echo "$BADGE" > $SUMMARY_WRITE_ROOT/tests/summary/"$CONNECTOR"/badge.json
  echo "$HTML" > $SUMMARY_WRITE_ROOT/tests/summary/"$CONNECTOR"/index.html

  aws s3 sync "$SUMMARY_WRITE_ROOT"/tests/summary/"$CONNECTOR"/ s3://"$BUCKET"/tests/summary/"$CONNECTOR"/
}

function main() {
  write_job_log
  pull_latest_job_logs
  write_badge_and_summary
}

main
