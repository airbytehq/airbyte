#!/usr/bin/env sh

echo Spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-dynamodb:dev spec
echo Check
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-dynamodb:dev check --config /secrets/config.json
echo Discover
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-dynamodb:dev discover --config /secrets/config.json
echo Read
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/source-dynamodb:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
