#!/usr/bin/env bash

set -e

echo "Writing cloud storage credentials.."
# write credentals to the right spot

echo "Running logging tests.."
./gradlew --no-daemon :airbyte-config:models:integrationTest  --scan
