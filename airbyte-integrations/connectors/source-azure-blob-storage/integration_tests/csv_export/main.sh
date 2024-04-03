#!/usr/bin/env bash

cd "$(dirname "$0")"

mkdir -p /tmp/csv
cp -r $(pwd) /tmp/csv

docker run --rm \
 -v /tmp/csv/csv_export/secret_faker:/secrets \
  -v /tmp/csv/csv_export/configured_catalog:/integration_tests \
  airbyte/source-faker:latest read \
  --config /secrets/secret_faker.json \
  --catalog /integration_tests/configured_catalog.json \
  | tee >(./purchases.sh) >(./products.sh) >(./users.sh) > /dev/null
