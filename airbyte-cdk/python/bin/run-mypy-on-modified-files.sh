set -e
git fetch origin master
git diff --name-only --relative --diff-filter=d master -- . | grep -E '\.py$' | xargs mypy --config-file mypy.ini --install-types --non-interactive