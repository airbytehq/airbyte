set -e
git diff --name-only --relative --diff-filter=d origin/master -- . | grep -E '\.py$' | xargs mypy --config-file mypy.ini --install-types --non-interactive