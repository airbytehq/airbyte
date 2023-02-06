#!/bin/bash

USAGE="
Usage: $(basename "$0") <source_connector_dir_name> <source_config_path>

Examples: 

./tools/erds/generator.sh source_stripe tools/erds/secrets/stripe.json
"

set -ex
. tools/lib/lib.sh
assert_root

ERD_OUTPUT_DIR=/tmp/erds-output-dir
CONNECTOR_DIR_NAME=
SOURCE_CONFIG_PATH=
CONNECTOR_IMAGE_NAME=
TMP_SOURCE_CONFIG_PATH=$ERD_OUTPUT_DIR/source_config.json
CATALOG_PATH=$ERD_OUTPUT_DIR/catalog.json
DESTINATION_CONFIG_PATH=$ERD_OUTPUT_DIR/destination_dummy_config.json

function build_normalization_image(){
  # building via gradle builds a bunch of unnecessary variants of the normalization image, so we run assemble to compile any code
  # then build the docker image directly
  SUB_BUILD=CONNECTORS_BASE ./gradlew :airbyte-integrations:bases:base-normalization:assemble
  echo "Building normalization dev image"
  cd airbyte-integrations/bases/base-normalization
  docker build . -t airbyte/normalization:dev
  cd -
}

function build_connector_image(){
  local connector_dir_name=$1
  cd airbyte-integrations/connectors/$connector_dir_name
  CONNECTOR_IMAGE_NAME=$(cat Dockerfile | grep io.airbyte.name | cut -d= -f2):dev
  echo "Building $CONNECTOR_IMAGE_NAME"
  docker build . -t $CONNECTOR_IMAGE_NAME
  cd -
}

function run() {
  # prep the tmp dir
  [ -d $ERD_OUTPUT_DIR ] && rm -rf $ERD_OUTPUT_DIR
  mkdir $ERD_OUTPUT_DIR
  echo '{"project_id": "erd_generator", "dataset_location": "public", "dataset_id": "public"}' > $DESTINATION_CONFIG_PATH
  cp $SOURCE_CONFIG_PATH $TMP_SOURCE_CONFIG_PATH

  # Generate the configured catalog
  build_connector_image $CONNECTOR_DIR_NAME
  cd ./tools/erds
  [ -d .venv ] || python -m venv .venv && source .venv/bin/activate && pip install .
  # Uncomment if something goes wrong
  docker run -v $ERD_OUTPUT_DIR:/erds $CONNECTOR_IMAGE_NAME discover --config /erds/source_config.json
  docker run -v $ERD_OUTPUT_DIR:/erds $CONNECTOR_IMAGE_NAME discover --config /erds/source_config.json | grep 'CATALOG'
  docker run -v $ERD_OUTPUT_DIR:/erds $CONNECTOR_IMAGE_NAME discover --config /erds/source_config.json | grep 'CATALOG' | python erd_generator/configured_catalog.py > $CATALOG_PATH
  cd -

  # Build normalization
  build_normalization_image
#  docker image inspect airbyte/normalization:dev >/dev/null 2>&1 && echo "Normalization dev image found - skipping the build" || build_normalization_image

  # Generate the ERD
  docker run -v $ERD_OUTPUT_DIR:/airbyte/models/ -v $ERD_OUTPUT_DIR:/inputs airbyte/normalization:dev configure-dbt --config /inputs/destination_dummy_config.json --catalog /inputs/catalog.json --integration-type bigquery

  # Print the output path, so consuming scripts can tail this script's stdout to get the path
  echo "$ERD_OUTPUT_DIR/generated/erd.dbml"
}

USAGE="
Usage: $(basename "$0") <source_connector_image_name> <source_config_path>
"

function main() {
  CONNECTOR_DIR_NAME=$1; shift || error "Missing source_connector_image_name $USAGE"
  SOURCE_CONFIG_PATH=$1; shift || error "Missing source_config_path $USAGE"
  run
}

main "$@"
