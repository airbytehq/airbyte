#!/bin/bash

connector=$1

set +e
echo "adding airbyte git remote"
git remote add airbyte https://github.com/airbytehq/airbyte.git
set -e

echo "fetching latest master"
git fetch airbyte master

echo "checking out airbyte-integrations/connectors/$connector from airbyte/master"
git checkout airbyte/master -- airbyte-integrations/connectors/$connector

echo "to build images for this image, you need to add this connector name to .github/workflows/connectors.yml"
echo "jobs.build_connectors.strategy.matrix.connector is the place to add the new connector"
