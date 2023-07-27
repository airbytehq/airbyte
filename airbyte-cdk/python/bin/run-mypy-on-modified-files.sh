set -e
# TODO change this to include unit_tests as well once it's in a good state
{ git diff --name-only --relative ':(exclude)unit_tests'; git diff --name-only --staged --relative ':(exclude)unit_tests'; git diff --name-only master... --relative ':(exclude)unit_tests'; } | grep -E '\.py$' | sort | uniq | xargs .venv/bin/python -m mypy --config-file mypy.ini --install-types --non-interactive
