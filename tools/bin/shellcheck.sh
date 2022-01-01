#!/usr/bin/env bash

set -e

# Ensure always run from the repo root
cd "$(dirname "${0}")/../.." || exit 1

SHELL_SCRIPTS="$(find . -type f -name '*.sh' -not -path './.git/*')"

# shellcheck disable=SC2086
shellcheck --external-sources ${SHELL_SCRIPTS}

# TODO: bash shell shebang
# TODO: github action
