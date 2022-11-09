#!/usr/bin/env bash

if [[ "${TRACE-0}" == "1" ]]; then set -o xtrace; fi
cd "$(dirname "$0")"

connector=$1

set +e
echo "adding airbyte git remote"
git remote add airbyte https://github.com/airbytehq/airbyte.git
set -e

echo "fetching latest master"
git fetch airbyte master

connector_dir="airbyte-integrations/connectors/$connector"
if [[ ! -d "$connector_dir" ]]; then
  echo "new connector, checking out $connector_dir from airbyte/master"
  git checkout airbyte/master -- $connector_dir

  echo "to build images for this image, you need to add this connector name to .github/workflows/connectors.yml"
  echo "jobs.build_connectors.strategy.matrix.connector is the place to add the new connector"
else
  echo "existing connector, comparing local version with airbyte/master"
  git worktree add master-upstream airbyte/master

  # -N makes diff output a similar line when a file exists in one directory but
  # not the other
  # -q makes diff only print the filenames and not the actual diff
  # -r recurses into directories
  # and we --exclude virtualenv directory to avoid noise
  different_files=$(diff -Nqr --exclude .venv $connector_dir master-upstream/$connector_dir | awk '{ print $2 }')
  for file in $different_files; do
    # if file does not exist in local, we just use the file from upstream
    if [[ ! -f "$file" ]]; then
      echo "New file found in airbyte/master: $file"
      mv "master-upstream/$file" "$file"
      continue
    fi
    set +e
    result="$(diff --color=always "$file" "master-upstream/$file")"
    set -e
    if [[ -n "$result" ]]; then
      echo "$file"
      echo "$result"
      echo "Lines starting with < are local and lines starting with > are from airbyte/master."
      echo "Which version would you like to keep? (< or >)"
      read version

      if [[ "$version" == "<" || "$version" == "local" ]]; then
        echo "Keeping local version of $file"
      elif [[ "$version" == ">" || "$version" == "remote" ]]; then
        echo "Replacing local version with version from airbyte/master."
        mv "master-upstream/$file" "$file"
      else
        echo "Invalid answer $version, expected < or >"
        exit 1
      fi
    fi
  done

  git worktree remove --force master-upstream
fi

