#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

assert_root

echo "Starting app..."

# todo (cgardens) - docker-compose 1.27.3 contained a bug that causes a failure if the volume path
#  does not exist when the volume is created. It was fixed in 1.27.4. Github actions virtual envs,
#  however, new ubuntu release upgraded to 1.27.3 on 09/24/20. Once github actions virtual envs
#  upgrades to 1.27.4, we can stop manually making the directory.
mkdir -p /tmp/airbyte_local

# todo (airbyte-jenny), once kube tests are stable, this can potentially be reintegrated to there.
# it is separate for now because the kube tests are experiencing transient failures.
echo "Running config persistence integration tests..."

SUB_BUILD=PLATFORM USE_EXTERNAL_DEPLOYMENT=true \
SECRET_STORE_GCP_CREDENTIALS=${SECRET_STORE_GCP_CREDENTIALS} \
SECRET_STORE_GCP_PROJECT_ID=${SECRET_STORE_GCP_PROJECT_ID} \
./gradlew :airbyte-config:config-persistence:integrationTest --rerun-tasks --scan
