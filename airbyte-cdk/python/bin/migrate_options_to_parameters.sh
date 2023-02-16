#!/usr/bin/env bash

echo "Starting migration"

[ -z "$ROOT_DIR" ] && exit 1

CONNECTORS_DIR=$ROOT_DIR/airbyte-integrations/connectors
CDK_DIR=$ROOT_DIR/airbyte-cdk/python/

for directory in $CONNECTORS_DIR/source-* ; do
  MANIFEST_DIRECTORY=$(basename $directory | tr - _)
  FILEPATH=$directory/$MANIFEST_DIRECTORY/manifest.yaml

  if test -f $FILEPATH; then
    echo "Migrating manifest located at $FILEPATH"

    # In place replacement of $options to $parameters
    sed -i '' -E 's/\$options/\$parameters/' $FILEPATH

    # In place replacement of options used in interpolated curly braces {{ }}
    sed -i '' -E 's/{{ options/{{ parameters/' $FILEPATH
  fi
done