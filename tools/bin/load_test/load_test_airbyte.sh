#!/usr/bin/env bash

<<comment
This script performs a load test against an existing Airbyte instance by calling the instance's API to create and sync new connections.
It is intended to work with any Airbyte instance (local or remote, docker or kube, OSS or Cloud). It authenticates using a special auth header
that requires port-forwarding. It stores connector and connection IDs that it creates in a local file. The script can be run in cleanup mode,
which means the script will delete every connector and connection ID that it created and stored in that file.
comment

cd "$(dirname "$0")"

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CLEAR='\033[0m'

showhelp() {
  echo -e """Usage $(dirname $0)/load_test_airbyte [OPTIONS]

  load_test_airbyte performs a load-test against an existing Airbyte instance.

  Available OPTIONs:

  ${CLEAR}-h
    ${GREEN}Display help

  ${CLEAR}-W <workspace id>
    ${GREEN}Specify the workspace ID where new connectors and connections should be created.
    Required.

  ${CLEAR}-H <hostname>
    ${GREEN}Specify the Airbyte API server hostname that the script should call to create new connectors and connections.
    Defaults to 'localhost'.

  ${CLEAR}-P <port>
    ${GREEN}Specify the port for the Airbyte server. If kube (ie. '-k' is provided), port-forwarding
    will be set up for the airbyte-server deployment using the provided <port> (ie. '8001:8001').
    Defaults to '8001'.

  ${CLEAR}-C <count>
    ${GREEN}Specify the number of connections that should be created by the script.
    Defaults to '1'.

  ${CLEAR}-T <minutes>
    ${GREEN}Specify the time in minutes that each connection should sync for.
    Defaults to '10'.

  ${CLEAR}-k
    ${GREEN}Indicate that the script is running against a kubernetes instance of Airbyte

  ${CLEAR}-N <namespace>
    ${GREEN}Specify the kubernetes namespace where the airbyte-server deployment exists g (ex. "ab").
    Only use with '-k' option.
    Defaults to 'default'.
  """ && exit 1
}

if [[ $# -eq 0 ]] ; then
    showhelp
    exit 0
fi

hostname=localhost
api_port=8001
num_connections=1
sync_minutes=10
kube=false
kube_namespace=default

while getopts "hW:H:P:C:T:kN:" options ; do
  case "${options}" in
    h)
      showhelp
      ;;
    W)
      workspace_id="${OPTARG}"
      ;;
    H)
      hostname="${OPTARG}"
      ;;
    P)
      api_port="${OPTARG}"
      ;;
    C)
      num_connections="${OPTARG}"
      ;;
    T)
      sync_minutes="${OPTARG}"
      ;;
    k)
      kube=true
      ;;
    N)
      if test "$kube" = true; then
        kube_namespace="${OPTARG}"
      else
        echo "error: -k must be set to use option -N"
        exit 1
      fi
      ;;
    *)
      showhelp
      ;;
  esac
done

if test -z "$workspace_id"; then
  echo "error: must set a workspace id with -W"
  exit 1
fi

echo "set workspace_id to ${workspace_id}"
echo "set hostname to ${hostname}"
echo "set api_port to ${api_port}"
echo "set num_connections to ${num_connections}"
echo "set sync_minutes to ${sync_minutes}"
echo "set kube to ${kube}"
echo "set kube_namespace to ${kube_namespace}"

# base64-encoded: {"user_id": "cloud-api", "email_verified": "true"}
api_header="eyJ1c2VyX2lkIjogImNsb3VkLWFwaSIsICJlbWFpbF92ZXJpZmllZCI6ICJ0cnVlIn0K"

# call the API with the endpoint passed as arg $1, and (optional) payload passed as arg $2
# example of calling the API with a payload:
#    callApi "destinations/list" "{\"workspaceId\":\"${workspace}\"}"
function callApi {
  curl -s -X POST -H 'Content-Type: application/json' -H "X-Endpoint-API-UserInfo: ${api_header}" -d "$2" "${hostname}:${api_port}/api/v1/$1"
}

function getE2ETestSourceDefinitionId {
  # call source_definitions/list and search response for E2E Test, get the ID.
  # local uses `source-e2e-test`, while cloud uses `source-e2e-test-cloud`
  export sourceDefinitionId=$(
    callApi "source_definitions/list" |
      jq -r '.sourceDefinitions[] |
        select(
          (.dockerRepository == "airbyte/source-e2e-test") or
          (.dockerRepository == "airbyte/source-e2e-test-cloud")
        ) |
        .sourceDefinitionId'
  )
}

function getE2ETestDestinationDefinition {
  export destinationDefinitionId=$(
    callApi "destination_definitions/list" |
      jq -r '.destinationDefinitions[] |
        select(
          (.dockerRepository == "airbyte/destination-e2e-test") or
          (.dockerRepository == "airbyte/destination-dev-null")
        ) |
        .destinationDefinitionId'
  )
}

function createSource {
  body=$(
    sed "
      s/replace_source_read_secs/$(( 60*sync_minutes ))/g ;
      s/replace_source_definition_id/$sourceDefinitionId/g ;
      s/replace_workspace_id/$workspace_id/g" source_spec.json |
    tr -d '\n' |
    tr -d ' '
  )

  export sourceId=$(
    callApi "sources/create" $body |
    jq -r '.sourceId'
  )

  #TODO write ID to file for future cleanup

}

function createDestination {
  body=$(
    sed "
      s/replace_destination_definition_id/$destinationDefinitionId/g ;
      s/replace_workspace_id/$workspace_id/g" destination_spec.json |
    tr -d '\n' |
    tr -d ' '
  )
  export destinationId=$(
    callApi "destinations/create" $body |
    jq -r '.destinationId'
  )

  #TODO write ID to file for future cleanup

}

function discoverSource {
  export sourceCatalogId=$(
    callApi "sources/discover_schema" "{\"sourceId\":\"$sourceId\",\"disable_cache\":true}" |
      jq -r '.catalogId'
  )
}

function createMultipleConnections {
  for i in $(seq 1 $num_connections)
  do
    echo "Creating connection number $i..."
    createConnection $i
  done
  echo "Finished creating $num_connections connections."
}

# Call the API to create a connection. Replace strings in connection_spec.json with real IDs.
# $1 arg is the connection count, which is used in the name of the created connection
function createConnection {
  body=$(
    sed "
      s/replace_source_id/$sourceId/g ;
      s/replace_destination_id/$destinationId/g ;
      s/replace_catalog_id/$sourceCatalogId/g ;
      s/replace_connection_name/load_test_connection_$1/g" connection_spec.json |
    tr -d '\n' |
    tr -d ' '
  )

  export connectionId=$(
    callApi "web_backend/connections/create" $body |
      jq -r '.connectionId'
  )

  #TODO write ID to file for future cleanup
}

function portForward {
  # if running against kubernetes, set up "kubectl port-forward airbyte-server 8001:8001 -n ab" or something similar
  # note that local kube doesn't run in the ab namespace, so that should be optional
  echo "implement me"
}



############
##  MAIN  ##
############
getE2ETestSourceDefinitionId
echo "Retrieved E2E Test Source Definition ID: ${sourceDefinitionId}"

getE2ETestDestinationDefinition
echo "Retrieved E2E Test Destination Definition ID: ${destinationDefinitionId}"

createSource
echo "Created Source with ID: ${sourceId}"

createDestination
echo "Created Destination with ID: ${destinationId}"

discoverSource
echo "Retrieved sourceCatalogId: ${sourceCatalogId}"

createMultipleConnections
