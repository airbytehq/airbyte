#!/usr/bin/env bash

set -e

# Wrap run script in a script so that we can lazy evaluate the value of APPLICATION. APPLICATION is
# set by the dockerfile that inherits base-java, so it cannot be evaluated when base-java is built.
# We also need to make sure that stdin of the script is piped to the stdin of the java application.
if [[ $A = --write ]]; then
  cat <&0 | /airbyte/bin/"$APPLICATION" "$@"
else
  /airbyte/bin/"$APPLICATION" "$@"
fi
