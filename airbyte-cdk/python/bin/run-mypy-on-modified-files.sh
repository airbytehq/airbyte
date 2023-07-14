set -e
git diff --name-only --relative --diff-filter=d remotes/origin/master -- . | grep -E '\.py$' | xargs .venv/bin/python -m mypy --config-file mypy.ini --install-types --non-interactive