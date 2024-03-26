#!/bin/bash
set -e

# Get the parent folder of this script
export AIRBYTE_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Mount the repo a Python docker container with the script 
docker build -t=airbyte-ci:dev ${AIRBYTE_ROOT}/airbyte-ci --platform=linux/arm64

# Run the airbyte-ci CLI
docker run -it -v ${AIRBYTE_ROOT}:/airbyte -v /var/run/docker.sock:/var/run/docker.sock --env-file=.env --env=GCP_GSM_CREDENTIALS airbyte-ci:dev $@
