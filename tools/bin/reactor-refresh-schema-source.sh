#!/usr/bin/env bash

set -e
which schema_generator > /dev/null
if [ $? != 0 ];then
  echo "schema_generator is not installed.  See https://github.com/airbytehq/airbyte/tree/master/tools/schema_generator/ for installation instructions"
  exit 1
fi
script_folder=$(dirname $0)
pushd $PWD > /dev/null
cd $script_folder
root=$(git rev-parse --show-toplevel 2>> /dev/null)
popd > /dev/null
source=$1
airbyte_config=$2
source_root="${root}/airbyte-integrations/connectors/source-${source}"
if [ ! -d "${source_root}" ];then
  echo "Invalid source specified . Source folder not found at ${source_root}"
  exit 1
fi

if [ -z "${airbyte_config}" ];then
  echo "airbyte config must be provided"
  exit 1
fi
if [ ! -f "${airbyte_config}" ];then
  echo "${airbyte_config} is not a valid path"
  exit 1
fi
pushd $PWD > /dev/null
cd $source_root
echo "refreshing catalog for source"
python main.py discover --config $airbyte_config | schema_generator --configure-catalog


echo "refreshing schemas for source. (note: This is fetching live data using the provided credentials. it may take a while."
cd source_commercetools
python ../main.py read --config $airbyte_config --catalog ../integration_tests/configured_catalog.json | schema_generator --infer-schemas
echo "Finished refreshing schemas.  NOTE: Some schemas have been tweaked and standardized by hand.  You probably only want to check in the new schema for the no stream that was added."
echo "$source_root/integration_tests/configured_catalog.json should be checked in along with any new schemas found at $source_root/source_${source}/schemas/"
popd > /dev/null