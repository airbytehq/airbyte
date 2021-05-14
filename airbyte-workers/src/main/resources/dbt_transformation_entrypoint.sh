#!/usr/bin/env bash
set -e

if [[ -f "/data/job/transform/git_repo/dbt_project.yml" ]]; then
  # Find profile name used in the custom dbt project:
  PROFILE_NAME=`cat "/data/job/transform/git_repo/dbt_project.yml" | grep "profile:" | sed -E "s/profile: *['\"](.*)['\"]/\1/"`
  mv /data/job/transform/profiles.yml /data/job/transform/profiles.txt
  # Refer to the appropriate profile name in the profiles.yml file
  echo "Regenerate profiles.yml file for profile: $PROFILE_NAME"
  cat /data/job/transform/profiles.txt | sed -E "s/normalize:/$PROFILE_NAME:/" > /data/job/transform/profiles.yml
  rm -f /data/job/transform/profiles.txt
else
  echo "git repo does not contain a dbt_project.yml file?"
fi
# Run custom dbt command
echo "Running: dbt $@"
dbt $@
