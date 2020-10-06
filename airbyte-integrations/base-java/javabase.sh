#!/usr/bin/env bash

set -e

# wrap run script in a script so that we can effectively lazy evaluate the value of APPLICATION.
bin/"$APPLICATION" "$@"