#!/bin/bash

set -x
set -e

. tools/lib/lib.sh

DBDOCS_TOKEN=$DBDOCS_TOKEN

USAGE="
Usage: $(basename $0) <connector_directory_name>

Example:
$(basename $0) source-facebook-marketing
"

# install dbdocs
function main() {
  [ -n $DBDOCS_TOKEN ] || error "Expected the DBDOCS_TOKEN env variable to be set!"
  local connector_name=$1; shift || error $USAGE

  # TODO include only allow-listed connectors

  local connector_directory="airbyte-integrations/connectors/$connector_name/"
  # assume config json is in secrets/config.json. If there is no config.json then error out
  local secret_path="$connector_directory/secrets/config.json"
  local image_name=$(cat "$connector_directory/Dockerfile" | grep io.airbyte.name | cut -d= -f2)

  local generate_script="$(dirname $0)/generator.sh"
  # dbml_path is the last line output from the previous script
  local dbml_path=$($generate_script $connector_name $secret_path | tail -n 1)
  echo $dbml_path
  DBDOCS_TOKEN=$DBDOCS_TOKEN dbdocs build $dbml_path --project=$connector_name
}

main "$@"
