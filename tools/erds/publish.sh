#!/bin/bash

set -ex

. tools/lib/lib.sh

DBDOCS_TOKEN=$DBDOCS_TOKEN

USAGE="
Usage: $(basename $0) <connector_directory_name>

Example:
$(basename $0) source-facebook-marketing
"

# install dbdocs
function main() {
  [[ -n $DBDOCS_TOKEN ]] || error "Expected the DBDOCS_TOKEN env variable to be set!"
  local connector_name=$1; shift || error $USAGE
  if [[ -z $(cat "$(dirname $0)/allowlist.txt" | grep -w ^$connector_name$) ]]
  then
     echo "Skipping ERD generation for $connector_name because it's not in the allowlist"
     exit 0
  fi

  local connector_directory="airbyte-integrations/connectors/$connector_name"
  # assume config json is in secrets/config.json. If there is no config.json then error out
  local secret_path="$connector_directory/secrets/config.json"
  local image_name=$(cat "$connector_directory/Dockerfile" | grep io.airbyte.name | cut -d= -f2)

  "$(dirname $0)/generator.sh" $connector_name $secret_path
  local dbml_path=/tmp/erds-output-dir/generated/erd.dbml
  DBDOCS_TOKEN=$DBDOCS_TOKEN dbdocs build $dbml_path --project=$connector_name
}

main "$@"
