set -e
# TODO change this to include unit_tests as well once it's in a good state
git diff --name-only --relative --diff-filter=d remotes/origin/master -- airbyte_cdk source_declarative_manifest | grep -E '\.py$' | xargs .venv/bin/python -m mypy --config-file mypy.ini --install-types --non-interactive