#!/usr/bin/env bash

set -e

YAML_DIR=airbyte-protocol/models/src/main/resources/airbyte_protocol
OUTPUT_DIR=airbyte-integrations/base-python/airbyte_protocol/models

FILES=$(cd ../../$YAML_DIR; ls -1 | grep yaml)
for f in $FILES
do
  FILE_WITHOUT_EXTENSION=""$(echo -n $f | cut -d'.' -f 1)
  docker run -v "$(pwd)"/../..:/airbyte airbyte/code-generator:dev \
    --input airbyte/"$YAML_DIR"/"$FILE_WITHOUT_EXTENSION".yaml \
    --output airbyte/"$OUTPUT_DIR"/"$FILE_WITHOUT_EXTENSION".py \
    --disable-timestamp
done
