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
  endpoint=$1
  payload=${2:-""}

  curl --silent \
   --request POST \
   --fail-with-body \
   --show-error \
   --header 'Content-Type: application/json' \
   --header "X-Endpoint-API-UserInfo: ${x_endpoint_header}" \
   --user "${BASIC_AUTH_USERNAME}:${BASIC_AUTH_PASSWORD}" \
   --data "${payload}" \
    "${hostname}:${api_port}/api/v1/${endpoint}"
}

function readFirstLineFromFile {
  echo "$(head -1 $1)"
}

function removeFirstLineFromFile {
  echo "$(sed -i '' -e '1d' $1)"
}

function setCleanupFilesForWorkspace {
  export CONNECTION_CLEANUP_FILE="cleanup/${1}_connection_ids.txt"
  export DESTINATION_CLEANUP_FILE="cleanup/${1}_destination_ids.txt"
  export SOURCE_CLEANUP_FILE="cleanup/${1}_source_ids.txt"

  echo "set connection cleanup file to     $CONNECTION_CLEANUP_FILE"
  echo "set destination cleanup file to    $DESTINATION_CLEANUP_FILE"
  echo "set source cleanup file to         $SOURCE_CLEANUP_FILE"
}
