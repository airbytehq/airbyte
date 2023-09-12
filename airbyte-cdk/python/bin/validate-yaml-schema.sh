#!/usr/bin/env bash

[ -z "$ROOT_DIR" ] && exit 1

CONNECTORS_DIR=$ROOT_DIR/airbyte-integrations/connectors
CDK_DIR=$ROOT_DIR/airbyte-cdk/python/

for directory in $CONNECTORS_DIR/source-* ; do
  MANIFEST_DIRECTORY=$(basename $directory | tr - _)
  SOURCE_NAME=${MANIFEST_DIRECTORY#source_}
  if test -f "$directory/$MANIFEST_DIRECTORY/manifest.yaml"; then
    cd $directory

    rm -rf .venv
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt > /dev/null 2>&1
    pip install -e ".[tests]" > /dev/null 2>&1
    pip install -e $CDK_DIR > /dev/null 2>&1

    python main.py spec > /dev/null 2>&1
    ret=$?
    if [ $ret -ne 0 ]; then
      echo "----Error for source $SOURCE_NAME"
    else
      echo "Source $SOURCE_NAME is fine"
    fi

    deactivate
    cd ..
  fi
done
