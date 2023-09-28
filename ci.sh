#!/bin/bash

# Get the parent folder of this script
export AIRBYTE_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"


# Mount the repo a Python docker container with the script 
docker build -t=airbyte-ci:dev ${AIRBYTE_ROOT}/airbyte-ci
docker run -it -v ${AIRBYTE_ROOT}:/airbyte --env-file=.env --env=GCP_GSM_CREDENTIALS airbyte-ci:dev $@
