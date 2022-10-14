#!/usr/bin/env bash

<<comment
This script performs a load test against an existing Airbyte instance by calling the instance's API to create and sync new connections.
It is intended to work with any Airbyte instance (local or remote, docker or kube, OSS or Cloud). It authenticates using a special auth header
that requires port-forwarding. It stores connector and connection IDs that it creates in a local file. The script can be run in cleanup mode,
which means the script will delete every connector and connection ID that it created and stored in that file.
comment

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
  # call source_definitions/list and search response for E2E Test, get the ID
  # uses startswith because Cloud's dockerRepository for the E2E Test source is actually airbyte/source-e2e-test-cloud
  export sourceDefinitionId=$(
    callApi "source_definitions/list" |
      jq '.sourceDefinitions[]
        | select(.dockerRepository | startswith("airbyte/source-e2e-test"))
        | .sourceDefinitionId'
  )
}

function createSource {
  # based on sync_minutes, figure out what to set for max_messages in the source spec's connectionConfiguration
  # write created sourceId to file for later cleanup
  echo "implement me"

}

function createDestination {
  # get the destination Definition ID, set it in the spec
  # write created destinationId to file for later cleanup
  echo "implement me"
}

function createConnection {
  # straightforward, just use the sourceId and destinationId that we created
  # two options: either make them 'manual' and have the script start it manually, or set a schedule of
  # something like 24 hours so that the sync starts as soon as it is created
  # in the future, could get fancy with cron scheduling and set them up to all start at the exact same moment,
  # maybe out of scope for MVP
  echo "implement me"
}

function portForward {
  # if running against kubernetes, set up "kubectl port-forward airbyte-server 8001:8001 -n ab" or something similar
  # note that local kube doesn't run in the ab namespace, so that should be optional
  echo "implement me"
}



function getMockApiDestinationDefinition {
  # call destination_definitions/list and search response for E2E Test, get the ID
  echo "implement me"
}

function createMultipleConnections {
  # based on input, call `createConnection()` n times
  echo "implement me"
}

############
##  MAIN  ##
############

getE2ETestSourceDefinitionId
echo "E2E Test Source Definition ID is ${sourceDefinitionId}"
