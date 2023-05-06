#!/usr/bin/env bash

set -e

# if IS_CAPTURE_HEAP_DUMP_ON_ERROR is set to true, then will capture Heap dump on OutOfMemory error
if [[ $IS_CAPTURE_HEAP_DUMP_ON_ERROR = true ]]; then

  arrayOfSupportedConnectors=("source-postgres" "source-mssql" "source-mysql" )

  # The heap dump would be captured only in case when java-based connector fails with OutOfMemory error
  if [[ " ${arrayOfSupportedConnectors[*]} " =~ " $APPLICATION " ]]; then
      JAVA_OPTS=$JAVA_OPTS" -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/data/dump.hprof"
      export JAVA_OPTS
      echo "Added JAVA_OPTS=$JAVA_OPTS"
      echo "APPLICATION=$APPLICATION"
  fi
fi

# Wrap run script in a script so that we can lazy evaluate the value of APPLICATION. APPLICATION is
# set by the dockerfile that inherits base-java, so it cannot be evaluated when base-java is built.
# We also need to make sure that stdin of the script is piped to the stdin of the java application.
if [[ $A = --write ]]; then
  cat <&0 | /airbyte/bin/"$APPLICATION" "$@"
else
  /airbyte/bin/"$APPLICATION" "$@"
fi
