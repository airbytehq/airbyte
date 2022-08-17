#!/usr/bin/env bash


filename='/Users/yevhen/Airbyte/projects/changed_files.txt'
n=1
while read changed_file; do

CHANGED_CONNECTOR_FILES_ARRAY=()


if [[ $changed_file == "airbyte-integrations/connectors/"* ]]; then
  IFS='/' read -ra changed_file_array <<< "$changed_file"
  CHANGED_CONNECTOR_FILES_ARRAY+=(${changed_file_array[2]})
fi

echo "${CHANGED_CONNECTOR_FILES_ARRAY[*]}"


n=$((n+1))
done < $filename