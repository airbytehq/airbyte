<<comment
This file contains common util functions for use in load testing scripts.
comment

echo "Loading utils from $0"

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CLEAR='\033[0m'

function callApi {
  # call the API with the endpoint passed as arg $1, and (optional) payload passed as arg $2
  # example of calling the API with a payload:
  #    callApi "destinations/list" "{\"workspaceId\":\"${workspace}\"}"

  curl -s -X POST -H 'Content-Type: application/json' -H "X-Endpoint-API-UserInfo: ${x_endpoint_header}" -d "$2" "${hostname}:${api_port}/api/v1/$1"
}

function readFirstLineFromFile {
  echo "$(head -1 $1)"
}

function removeFirstLineFromFile {
  echo "$(sed -i '' -e '1d' $1)"
}

function setCleanupFilesForWorkspace {
  export connection_cleanup_file="cleanup/${1}_connection_ids.txt"
  export destination_cleanup_file="cleanup/${1}_destination_ids.txt"
  export source_cleanup_file="cleanup/${1}_source_ids.txt"

  echo "set connection cleanup file to $connection_cleanup_file"
  echo "set destination cleanup file to $destination_cleanup_file"
  echo "set source cleanup file to $source_cleanup_file"
}
