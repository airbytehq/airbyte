#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

assert_root

## Helper functions

get_epoch_time() {
  date +'%s'
}

check_success() {
  docker compose ps --all | grep "^$1" | grep -ie 'exit 0' -ie 'exited (0)' >/dev/null || (echo "$1 didn't run successfully"; exit 1)
}

##

echo "Starting app..."

# Detach so we can run subsequent commands
# NOTE: this passes APPLY_FIELD_SELECTION=true, which enables a feature -- field selection -- which is currently disabled by default.
# We want to run our CI tests against the new feature while we prepare to release it.
VERSION=dev TRACKING_STRATEGY=logging USE_STREAM_CAPABLE_STATE=true BASIC_AUTH_USERNAME="" BASIC_AUTH_PASSWORD="" APPLY_FIELD_SELECTION=true docker compose -f docker-compose.yaml -f docker-compose.acceptance-test.yaml up -d

# Sometimes source/dest containers using airbyte volumes survive shutdown, which need to be killed in order to shut down properly.
shutdown_cmd="docker compose down -v || docker kill \$(docker ps -a -f volume=airbyte_workspace -f volume=airbyte_data -f volume=airbyte_db -q) && docker compose down -v"
# Uncomment for debugging. Warning, this is verbose.
# trap "echo 'docker compose logs:' && docker compose logs -t --tail 1000 && $shutdown_cmd" EXIT

echo "Waiting for services to begin"
starttime=`get_epoch_time`
maxtime=300
while [[ "$(curl -s -o /dev/null -w ''%{http_code}'' localhost:8000/api/v1/health)" != "200" ]];
do
  echo "Waiting for docker deployment.."
  currenttime=`get_epoch_time`
  if [[ $(( $currenttime - $starttime )) -gt $maxtime ]]; then
    docker compose ps
    echo "Platform is taking more than ${maxtime}s to start. Aborting..."
    exit 1
  fi
  sleep 5
done

# Getting a snapshot of the docker compose state
docker compose ps

# Make sure init containers ran successfully
check_success 'init'
check_success 'airbyte-bootloader'

echo "Running e2e tests via gradle"
SUB_BUILD=PLATFORM USE_EXTERNAL_DEPLOYMENT=true ./gradlew :airbyte-tests:acceptanceTests --rerun-tasks --scan
