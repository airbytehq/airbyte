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

    sed -i '' -E 's/\field_pointer:/\field_path:/' $FILEPATH
  fi
done
