#!/bin/bash

USAGE="
Usage: $(basename "$0") <source_connector_image_name> <source_config_path>
"

set -e
. tools/lib/lib.sh
assert_root

ERD_OUTPUT_DIR=/tmp/erds-output-dir
CONNECTOR_IMAGE_NAME=
SOURCE_CONFIG_PATH=
TMP_SOURCE_CONFIG_PATH=$ERD_OUTPUT_DIR/source_config.json
CATALOG_PATH=$ERD_OUTPUT_DIR/catalog.json
DESTINATION_CONFIG_PATH=$ERD_OUTPUT_DIR/destination_dummy_config.json

function build_normalization_image(){
  # building via gradle builds a bunch of unnecessary variants of the normalization image
  echo "Building normalization dev image"
  cd airbyte-integrations/bases/base-normalization
  docker build . -t airbyte/normalization:dev
  cd -
}

function run() {
  # prep the tmp dir
  [ -d $ERD_OUTPUT_DIR ] && rm -rf $ERD_OUTPUT_DIR
  mkdir $ERD_OUTPUT_DIR
  echo '{"project_id": "erd_generator", "dataset_location": "public", "dataset_id": "public"}' > $DESTINATION_CONFIG_PATH
  cp $SOURCE_CONFIG_PATH $TMP_SOURCE_CONFIG_PATH

  # Generate the configured catalog
  cd ./tools/erds
  [ -d .venv ] || python -m venv .venv && source .venv/bin/activate && pip install .
  docker run -v $ERD_OUTPUT_DIR:/erds $CONNECTOR_IMAGE_NAME:dev discover --config /erds/source_config.json | grep 'CATALOG' | python erd_generator/configured_catalog.py > $CATALOG_PATH
  cd -

  # Build normalization
  build_normalization_image
#  docker image inspect airbyte/normalization:dev >/dev/null 2>&1 && echo "Normalization dev image found - skipping the build" || build_normalization_image

  # Generate the ERD
  docker run -v $ERD_OUTPUT_DIR:/airbyte/models/ -v $ERD_OUTPUT_DIR:/inputs airbyte/normalization:dev configure-dbt --config /inputs/destination_dummy_config.json --catalog /inputs/catalog.json --integration-type bigquery

  echo "DBML has been output to: $ERD_OUTPUT_DIR/generated/erd.dbml"
}

USAGE="
Usage: $(basename "$0") <source_connector_image_name> <source_config_path>
"

function main() {
  CONNECTOR_IMAGE_NAME=$1; shift || error "Missing source_connector_image_name $USAGE"
  SOURCE_CONFIG_PATH=$1; shift || error "Missing source_config_path $USAGE"
  run
}

main "$@"
