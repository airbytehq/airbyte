#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

while read -r var1 && read -r var2; do
    versioned_image="$var1:$var2"
    # publish spec to cache. do so, by running get spec locally and then pushing it to gcs.
    tmp_spec_file=$(mktemp)
    docker run --rm "$versioned_image" spec | \
      # 1. filter out any lines that are not valid json.
      jq -R "fromjson? | ." | \
      # 2. grab any json that has a spec in it.
      # 3. if there are more than one, take the first one.
      # 4. if there are none, throw an error.
      jq -s "map(select(.spec != null)) | map(.spec) | first | if . != null then . else error(\"no spec found\") end" \
      > "$tmp_spec_file"

    echo "uploading: $versioned_image"

     gsutil cp "$tmp_spec_file" gs://io-airbyte-cloud-spec-cache/specs/"$var1"/"$var2"/spec.json

done < <(echo "airbyte/destination-databricks" && echo "0.1.0")
