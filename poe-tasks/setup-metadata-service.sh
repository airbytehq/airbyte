#!/usr/bin/env bash
set -euo pipefail

source "${BASH_SOURCE%/*}/lib/util.sh"

poetry install --directory $METADATA_SERVICE_PATH
