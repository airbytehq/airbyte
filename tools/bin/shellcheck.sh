#!/usr/bin/env bash

set -e

# Ensure always run from the repo root
cd "$(dirname "${0}")/../.." || exit 1

# Every shell script except for generated files
SHELL_SCRIPTS="$(find . -type f -name '*.sh' -not -path './.git/*' -not -path './airbyte-webapp/node_modules/**' -not -path './airbyte-webapp/.gradle/**')"

# shellcheck disable=SC2086
shellcheck --external-sources ${SHELL_SCRIPTS}

# TODO: bash shell shebang
# TODO: github action
