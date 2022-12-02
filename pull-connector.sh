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

  echo "You need to make sure the Dockerfile of this connector uses airbyte-to-flow, see other connectors as an example"
  echo "Update the io.airbyte.version to be in the format of v1"
  echo "Update the ENTRYPOINT and add a line before it like so:"
  echo "  COPY --from=ghcr.io/estuary/airbyte-to-flow:dev /airbyte-to-flow ./"
  echo '  ENTRYPOINT ["/airbyte/integration_code/airbyte-to-flow", "--connector-entrypoint", "python /airbyte/integration_code/main.py"]'
  echo "Add these two lines to the end of the Dockerfile:"
  echo '  LABEL FLOW_RUNTIME_PROTOCOL=capture'
  echo '  LABEL CONNECTOR_PROTOCOL=flow-capture'
  echo ""
  echo "If you intend to patch the connector, these files can be placed in the root directory of the connector"
  echo "and copied in Dockerfile. The following files are supported:"
  echo "spec.patch.json -> to patch the connector's endpoint_spec, the patch is applied per RFC7396 JSON Merge"
  echo "spec.map.json -> to map fields from endpoint_spec. Keys and values are JSON pointers. Each key: value in this file is processed by moving whatever is at the value pointer to the key pointer"
  echo "oauth2.patch.json -> to patch the connector's oauth2 spec. This patch overrides the connector's oauth2 spec"
  echo "documentation_url.patch.json -> to patch the connector's documentation_url. Expects a single key with a string value \`documentation_url\`"
  echo "streams/<stream-name>.patch.json -> to patch a specific stream's document schema"
  echo "streams/<stream-name>.pk.json -> to patch a specific stream's primary key, expects an array of strings"
  echo ""
  echo "To add these patches to the Dockerfile, use the snippets below:"
  echo "COPY documentation_url.patch.json ./"
  echo "COPY spec.patch.json ./"
  echo "COPY spec.map.json ./"
  echo "COPY oauth2.patch.json ./"
  echo "COPY streams/* ./streams/"
  echo ""
  echo "Also make sure these files are not ignored by docker by adding the lines below to .dockerignore"
  echo "!*.patch.json"
  echo "!*.map.json"
  echo "!streams"
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

