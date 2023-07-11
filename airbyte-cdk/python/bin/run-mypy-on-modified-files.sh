set -e

if [ $# -gt 0 ]; then
  filesToDiff=("$@")
else
  filesToDiff=$(git diff --name-only --relative --diff-filter=d remotes/origin/master -- . | grep -E '\.py$')
fi

# .venv/bin is automatically created by gradle build
.venv/bin/python -m mypy --config-file mypy.ini --install-types --non-interactive $filesToDiff