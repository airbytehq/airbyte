#!/usr/bin/env bash

set -e

# Ensure always run from the repo root
cd "$(dirname "${0}")/../.." || exit 1

SHELL_SCRIPTS="$(find . -type f -name '*.sh')"

# shellcheck -f diff ${SHELL_SCRIPTS} | git apply --unsafe-paths

# shellcheck disable=SC2086
shellcheck ${SHELL_SCRIPTS}

# TODO: bash shell shebang
# TODO: github action
