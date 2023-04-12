#!/usr/bin/env bash

# Ideally we'd like to have set -e, but when set -e is used, the `python -m pytest unit_tests` command can return a
# non-zero exit code and end the whole script prematurely
# set -e

[ -z "$ROOT_DIR" ] && exit 1

CONNECTORS_DIR=$ROOT_DIR/airbyte-integrations/connectors
CDK_DIR=$ROOT_DIR/airbyte-cdk/python/

for directory in $CONNECTORS_DIR/source-* ; do
  MANIFEST_DIRECTORY=$(basename $directory | tr - _)
  SOURCE_NAME=${MANIFEST_DIRECTORY#source_}
  if test -f "$directory/$MANIFEST_DIRECTORY/manifest.yaml"; then
    cd $directory

    # Unit tests are optional for most connectors unless they implement custom components
    if [ -d "unit_tests" ]; then
      rm -rf .venv
      python -m venv .venv
      source .venv/bin/activate
      pip install -r requirements.txt > /dev/null 2>&1
      pip install -e ".[tests]" > /dev/null 2>&1
      pip install -e $CDK_DIR > /dev/null 2>&1

      test_output=$(python -m pytest unit_tests)
      ret=$?
      if [[ "$test_output" == *"no tests ran"* ]]; then
        # When there are no tests defined, code 5 gets emitted so we should also check test output for no tests run
        echo "Source $SOURCE_NAME did not have any tests"
      elif [ $ret -ne 0 ]; then
        echo "----Tests failed for source $SOURCE_NAME"
      else
        echo "Source $SOURCE_NAME passed tests"
      fi

      deactivate
      cd ..
    fi
  fi
done
