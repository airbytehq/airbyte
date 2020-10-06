#!/usr/bin/env bash

set -e

# wrap run script in a script so that we can lazy evaluate the value of APPLICATION. APPLICATION is
# set by the dockerfile that inherits base-java, so it cannot be evaluated when base-java is built.
cat <&0 | bin/"$APPLICATION" "$@"
