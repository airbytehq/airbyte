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

  ${CLEAR}-w <workspace id>
      ${GREEN}Specify the workspace ID where new connectors and connections should be created

  ${CLEAR}-s <hostname>
    ${GREEN}Specify the Airbyte API server hostname that the script should call to create new connectors and connections

  ${CLEAR}-p <port mapping>
    ${GREEN}Specify the kubernetes airbyte-server deployment port-forward mapping (ex. "8001:8001 -n ab")

  ${CLEAR}-n <count>
    ${GREEN}Specify the number of connections that should be created by the script

  ${CLEAR}-t <minutes>
    ${GREEN}Specify the time in minutes that each connection should sync for

  ${CLEAR}-c
    ${GREEN}Run in cleanup mode instead of creating new syncs. Previously-created connectors and connections will be deleted.
  """ && exit 1
}

if [[ $# -eq 0 ]] ; then
    showhelp
    exit 0
fi

while getopts ":hw:s:p:n:t:c" options ; do
  case "${options}" in
    h)
      showhelp
      ;;
    w)
      workspace="${OPTARG}"
      ;;
    s)
      server="${OPTARG}"
      ;;
    p)
      port_mapping="${OPTARG}"
      ;;
    n)
      num_connections="${OPTARG}"
      ;;
    t)
      sync_minutes="${OPTARG}"
      ;;
    c)
      cleanup=true
      ;;
    *)
      showhelp
      ;;
  esac
done

echo "set server to ${server}"
echo "set workspace to ${workspace}"
echo "set port_mapping to ${port_mapping}"
echo "set num_connections to ${num_connections}"
echo "set sync_minutes to ${sync_minutes}"
echo "set cleanup to ${cleanup}"

# base64-encoded: {"user_id": "cloud-api", "email_verified": "true"}
api_header="eyJ1c2VyX2lkIjogImNsb3VkLWFwaSIsICJlbWFpbF92ZXJpZmllZCI6ICJ0cnVlIn0K"

function createSource() {
  # based on sync_minutes, figure out what to set for max_messages in the source spec's connectionConfiguration
  # write created sourceId to file for later cleanup
}

function createDestination() {
  # get the destination Definition ID, set it in the spec
  # write created destinationId to file for later cleanup

}

function createConnection() {
  # straightforward, just use the sourceId and destinationId that we created
  # two options: either make them 'manual' and have the script start it manually, or set a schedule of
  # something like 24 hours so that the sync starts as soon as it is created
  # in the future, could get fancy with cron scheduling and set them up to all start at the exact same moment,
  # maybe out of scope for MVP

}

function portForward() {
  # if running against kubernetes, set up "kubectl port-forward airbyte-server 8001:8001 -n ab" or something similar
  # note that local kube doesn't run in the ab namespace, so that should be optional

}

function getMockApiSourceDefinition() {
  # call source_definitions/list and search response for Mock API, get the ID
}

function getMockApiDestinationDefinition() {
  # call destination_definitions/list and search response for E2E Test, get the ID
}

function createMultipleConnections() {
  # based on input, call `createConnection()` n times
}

function cleanup() {
  # go through files of IDs that were created previously, call API to delete connectors/connections

}

# main
