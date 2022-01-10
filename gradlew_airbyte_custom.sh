#!/bin/sh

# Custom gradle wrapper functionality to add into gradlew. Because gradlew is a wrapper managed by gradle
# we should not really be putting any code in there as upon upgrades the file will be overwritten.
# However in order to better handle targeted gradle builds with respect to connector gradle projects
# there is really no great way to do this without some sort of additional wrapping functionality.

# This env flag is set in order to tell gradle that this file has been sourced by gradlew. This is here purely
# to remind people upgrading gradlew to add back in this script to the newly generated gradlew file.
export GRADLEW_AIRBYTE_CUSTOM="true"

# Add this in gradlew by putting ". ./gradlew_airbyte_custom.sh" anywhere in the file

# Check if the gradle task is a connector, if so, set INCLUDE_CONNECTORS so settings.gradle can
# conditionally include connector subprojects. Since settings.gradle is evaluated before any build.gradle
# files, we can't really make any of the includes conditional based on task/project name variables that
# Gradle sets _for_ us. So we have to make a light wrapper around gradle commands and check for an environment variable
# this script will set if necessary.
#
# The regex match allows alphanumerics and dashes
INCLUDE_CONNECTOR=$(echo "$*" | grep -E -o ":airbyte-integrations:connectors:[a-z0-9\-]+")
if [ -n "${INCLUDE_CONNECTOR}" ]; then
  export INCLUDE_CONNECTOR
fi
