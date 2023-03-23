#!/usr/bin/env bash

# Read input params
read -r -p 'Enter connector name: ' connector
read -r -p 'Enter first connector version: ' version_1
read -r -p 'Enter second connector version: ' version_2

printf "\nPulling connectors images:\n"

docker pull airbyte/"$connector":"$version_1"
docker pull airbyte/"$connector":"$version_2"

printf "\nStarting comparing connector %s version %s with version %s:\n" "$connector" "$version_1" "$version_2"


run_docker_image()
{
  echo docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/"$connector":"$version" read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
}

result=$( diff <(run_docker_image "$connector", "$version_1") <(run_docker_image "$connector", "$version_2") | grep 'RECORD' | sed '/\"emitted_at\"/,/}/ d')

if [ -n "$result" ]; then
    printf "%s" "$result"
    printf "Records output not equal."
else
    printf "Records output equal."
fi