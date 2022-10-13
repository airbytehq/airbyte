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

# Detach so we can run subsequent commands
VERSION=dev TRACKING_STRATEGY=logging docker-compose up -d
# Uncomment for debugging. Warning, this is verbose.
# trap 'echo "docker-compose logs:" && docker-compose logs -t --tail 1000 && docker-compose down && docker stop airbyte_ci_pg' EXIT

docker run --rm -d -p 5433:5432 -e POSTGRES_PASSWORD=secret_password -e POSTGRES_DB=airbyte_ci --name airbyte_ci_pg postgres
echo "Waiting for health API to be available..."
# Retry loading the health API of the server to check that the server is fully available
until $(curl --output /dev/null --fail --silent --max-time 5 --head localhost:8001/api/v1/health); do
  echo "Health API not available yet. Retrying in 10 seconds..."
  sleep 10
done

echo "Running e2e tests via gradle"
SUB_BUILD=PLATFORM ./gradlew --no-daemon :airbyte-webapp-e2e-tests:e2etest -PcypressWebappKey=$CYPRESS_WEBAPP_KEY
