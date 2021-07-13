#!/usr/bin/env bash
set -e

CWD=$(pwd)
if [[ -f "${CWD}/git_repo/dbt_project.yml" ]]; then
  # Find profile name used in the custom dbt project:
  PROFILE_NAME=$(grep -e "profile:" < "${CWD}/git_repo/dbt_project.yml" | sed -E "s/profile: *['\"]?([^'\"]*)['\"]?/\1/")
  if [[ -n "${PROFILE_NAME}" ]]; then
    mv "${CWD}/profiles.yml" "${CWD}/profiles.txt"
    # Refer to the appropriate profile name in the profiles.yml file
    echo "Regenerate profiles.yml file for profile: $PROFILE_NAME"
    sed -E "s/normalize:/$PROFILE_NAME:/" < "${CWD}/profiles.txt" > "${CWD}/profiles.yml"
    rm -f "${CWD}/profiles.txt"
    if [[ -f "${CWD}/bq_keyfile.json" ]]; then
      cp "${CWD}/bq_keyfile.json" /tmp/bq_keyfile.json
    fi
  fi
else
  echo "git repo does not contain a dbt_project.yml file?"
fi
# Detect if some mandatory dbt flags were already passed as arguments
CONTAINS_PROFILES_DIR="false"
CONTAINS_PROJECT_DIR="false"
for var in "$@"; do
    if [[ -n $(echo "${var}" | grep -e "--profiles-dir=") ]]; then
      CONTAINS_PROFILES_DIR="true"
    fi
    if [[ -n $(echo "${var}" | grep -e "--project-dir=") ]]; then
      CONTAINS_PROJECT_DIR="true"
    fi
done
# Add mandatory flags profiles-dir and project-dir when calling dbt when necessary
if [[ "${CONTAINS_PROFILES_DIR}" = "true" ]]; then
  if [[ "${CONTAINS_PROJECT_DIR}" =  "true" ]]; then
    echo "Running: dbt $@"
    dbt $@
  else
    echo "Running: dbt $@ --project-dir=${CWD}/git_repo"
    dbt $@ "--project-dir=${CWD}/git_repo"
  fi
else
  if [[ "${CONTAINS_PROJECT_DIR}" =  "true" ]]; then
    echo "Running: dbt $@ --profiles-dir=${CWD}"
    dbt $@ "--profiles-dir=${CWD}"
  else
    echo "Running: dbt $@ --profiles-dir=${CWD} --project-dir=${CWD}/git_repo"
    dbt $@ "--profiles-dir=${CWD}" "--project-dir=${CWD}/git_repo"
  fi
fi
