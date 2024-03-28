#!/usr/bin/env bash

cd "$(dirname "$0")"

mkdir -p /tmp/csv


docker run --rm -v $(pwd)/secret_faker:/secrets -v $(pwd)/configured_catalog:/integration_tests airbyte/source-faker:latest read --config /secrets/secret_faker.json --catalog /integration_tests/configured_catalog.json\
  | tee >(./purchases.sh) >(./products.sh) >(./users.sh)
