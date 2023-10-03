#!/usr/bin/env sh

set -e

# Ensure script always runs from the project directory.
cd "$(dirname "${0}")/.." || exit 1

# TODO change this to include unit_tests as well once it's in a good state
{
  git diff --name-only --relative ':(exclude)unit_tests'
  git diff --name-only --staged --relative ':(exclude)unit_tests'
  git diff --name-only master... --relative ':(exclude)unit_tests'
} | grep -E '\.py$' | sort | uniq | xargs .venv/bin/python -m mypy --config-file mypy.ini --install-types --non-interactive
