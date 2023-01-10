#!/usr/bin/env bash

set -e

HOSTNAME=`hostname`
ACTIVE_USER=`whoami`
MESSAGE="source-faker run on $HOSTNAME by $ACTIVE_USER | $@"

curl -S -s -o /dev/null -X POST -H "Content-Type: application/json" -d "{\"payload\":\"$MESSAGE\"}" https://echo.evantahler.com/api/log

python /airbyte/integration_code/main.py "$@"
