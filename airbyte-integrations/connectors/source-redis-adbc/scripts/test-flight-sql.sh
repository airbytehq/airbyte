#!/usr/bin/env bash
# Test against Apache's pinned SQLite reference Flight SQL server.
set -euo pipefail
cd "$(dirname "$0")/.."
suffix="$$"
network="airbyte-flight-test-$suffix"
server="airbyte-flight-server-$suffix"
cleanup() {
    docker rm -f "$server" >/dev/null 2>&1 || true
    docker network rm "$network" >/dev/null 2>&1 || true
}
trap cleanup EXIT
docker build -f integration_tests/flight_sql/Dockerfile -t airbyte-flight-reference:18.8.0 .
bash scripts/build-image.sh
docker build -f Dockerfile.test -t airbyte-redis-adbc-test:dev .
docker network create "$network" >/dev/null
docker run -d --name "$server" --network "$network" airbyte-flight-reference:18.8.0 >/dev/null
for attempt in $(seq 1 60); do
    if docker logs "$server" 2>&1 | grep -q 'Starting SQLite Flight SQL Server'; then break; fi
    sleep 1
done
docker run --rm --network "$network" \
    -e FLIGHT_SQL_URI="grpc://$server:31337" \
    airbyte-redis-adbc-test:dev -q integration_tests/test_flight_sql.py
