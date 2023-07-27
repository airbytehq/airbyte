set -e
# TODO change this to include unit_tests as well once it's in a good state
git diff --name-only master... ':(exclude)unit_tests' | xargs -I '{}' realpath --relative-to=. $(git rev-parse --show-toplevel)/'{}' | grep -E '\.py$' | xargs .venv/bin/python -m mypy --config-file mypy.ini --install-types --non-interactive