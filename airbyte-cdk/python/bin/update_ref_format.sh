#!/usr/bin/env bash

[ -z "$ROOT_DIR" ] && exit 1

CONNECTORS_DIR=$ROOT_DIR/airbyte-integrations/connectors
CDK_DIR=$ROOT_DIR/airbyte-cdk/python/

for directory in $CONNECTORS_DIR/source-* ; do
  MANIFEST_DIRECTORY=$(basename $directory | tr - _)
  SOURCE_NAME=${MANIFEST_DIRECTORY#source_}
  FILEPATH=$directory/source_$SOURCE_NAME/$SOURCE_NAME.yaml
  if test -f $FILEPATH; then
    gsed -i -E 's/\*ref\((.*)\)/#\/\1/' $FILEPATH
    gsed -i -E '/#\//  y/./\//' $FILEPATH
  fi
done
