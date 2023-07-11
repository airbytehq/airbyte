set -e
git fetch origin master
# .venv/bin is automatically created by gradle build
git diff --name-only --relative --diff-filter=d remotes/origin/master -- . | grep -E '\.py$' | xargs .venv/bin/python -m mypy --config-file mypy.ini --install-types --non-interactive