#!/usr/bin/env bash

echo "Starting migration"

[ -z "$ROOT_DIR" ] && exit 1

CONNECTORS_DIR=$ROOT_DIR/airbyte-integrations/connectors
CDK_DIR=$ROOT_DIR/airbyte-cdk/python/

for directory in $CONNECTORS_DIR/source-* ; do
  MANIFEST_DIRECTORY=$(basename $directory | tr - _)
  SOURCE_NAME=${MANIFEST_DIRECTORY#source_}
  FILEPATH=$directory/source_$SOURCE_NAME/$SOURCE_NAME.yaml

  echo "Migrating manifest located at $FILEPATH"
  if test -f $FILEPATH; then
    # In place replacement of $options to $parameters
    sed -i '' -E 's/\$options/\$parameters/' $FILEPATH

    # In place replacement of options used in interpolated curly braces {{ }}
    sed -i '' -E 's/{{ options/{{ parameters/' $FILEPATH
  fi
done