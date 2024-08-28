#!/usr/bin/env bash
set -e

CWD=$(pwd)
# change directory to be inside git_repo that was just cloned
cd git_repo
echo "Running from $(pwd)"
POSITIONAL=()
# Detect if some mandatory dbt flags were already passed as arguments
CONTAINS_PROFILES_DIR="false"
CONTAINS_PROJECT_DIR="false"
while [[ $# -gt 0 ]]; do
  case $1 in
    --profiles-dir=*|--profiles-dir)
      CONTAINS_PROFILES_DIR="true"
      POSITIONAL+=("$1")
      shift
      ;;
    --project-dir=*|--project-dir)
      CONTAINS_PROJECT_DIR="true"
      POSITIONAL+=("$1")
      shift
      ;;
    *)
      POSITIONAL+=("$1")
      shift
      ;;
  esac
done

set -- "${POSITIONAL[@]}"

if [[ -f "${CWD}/bq_keyfile.json" ]]; then
  cp "${CWD}/bq_keyfile.json" /tmp/bq_keyfile.json
fi

. $CWD/sshtunneling.sh
openssh $CWD/ssh.json
trap 'closessh' EXIT

# Add mandatory flags profiles-dir and project-dir when calling dbt when necessary
case "${CONTAINS_PROFILES_DIR}-${CONTAINS_PROJECT_DIR}" in
  true-true)
    echo "Running: dbt $@"
    dbt $@ --profile normalize
    ;;
  true-false)
    echo "Running: dbt $@ --project-dir=${CWD}/git_repo"
    dbt $@ "--project-dir=${CWD}/git_repo" --profile normalize
    ;;
  false-true)
    echo "Running: dbt $@ --profiles-dir=${CWD}"
    dbt $@ "--profiles-dir=${CWD}" --profile normalize
    ;;
  *)
    echo "Running: dbt $@ --profiles-dir=${CWD} --project-dir=${CWD}/git_repo"
    dbt $@ "--profiles-dir=${CWD}" "--project-dir=${CWD}/git_repo" --profile normalize
    ;;
esac

closessh
