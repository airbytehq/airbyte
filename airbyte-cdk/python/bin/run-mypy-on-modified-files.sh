#!/usr/bin/env sh

set -e

# Ensure script always runs from the project directory.
cd "$(dirname "${0}")/.." || exit 1

if [ "$#" -gt 0 ]; then
  # Usually CI: if files are provided as arguments, run mypy directly on those files.
  mypy --config-file pyproject.toml -- "$@"
else
  # Usually local: if no files are provided, calculate the diff and run mypy on the result.
  {
    git diff --name-only --diff-filter=d --relative ':(exclude)unit_tests'
    git diff --name-only --diff-filter=d --staged --relative ':(exclude)unit_tests'
    git diff --name-only --diff-filter=d master... --relative ':(exclude)unit_tests'
  } | grep -E '\.py$' | sort | uniq | xargs mypy --config-file pyproject.toml --install-types --non-interactive
fi
