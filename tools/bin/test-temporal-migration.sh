#! /bin/bash

set -ex

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

while getopts o:t: params
do
  case "${params}" in
    o) originalVersion=${OPTARG};;
    t) targetVersion=${OPTARG};;
  esac
done

mkdir /tmp/old-docker-compose

"SUB_BUILD=PLATFORM $SCRIPT_DIR/../../gradlew assemble"

curl https://raw.githubusercontent.com/airbytehq/airbyte/master/docker-compose.debug.yaml > /tmp/old-docker-compose.yaml
