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
#30781 - Allocate 32KB for log4j appender buffer to ensure that each line is logged in a single println
JAVA_OPTS=$JAVA_OPTS" -Dlog4j.encoder.byteBufferSize=32768 -Dlog4j2.configurationFile=log4j2.xml"
#needed because we make ThreadLocal.get(Thread) accessible in IntegrationRunner.stopOrphanedThreads
JAVA_OPTS=$JAVA_OPTS" --add-opens=java.base/java.lang=ALL-UNNAMED"
# tell jooq to be quiet (https://stackoverflow.com/questions/28272284/how-to-disable-jooqs-self-ad-message-in-3-4)
JAVA_OPTS=$JAVA_OPTS" -Dorg.jooq.no-logo=true -Dorg.jooq.no-tips=true"
export JAVA_OPTS

# Wrap run script in a script so that we can lazy evaluate the value of APPLICATION. APPLICATION is
# set by the dockerfile that inherits base-java, so it cannot be evaluated when base-java is built.
# We also need to make sure that stdin of the script is piped to the stdin of the java application.
if [[ $A = --write ]]; then
  cat <&0 | /airbyte/bin/"$APPLICATION" "$@"
else
  /airbyte/bin/"$APPLICATION" "$@"
fi
