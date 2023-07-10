set -e
git ls-remote --heads origin master
git fetch origin master
git branch -a
git diff --name-only --relative --diff-filter=d master -- . | grep -E '\.py$' | xargs mypy --config-file mypy.ini --install-types --non-interactive