#!/usr/bin/env bash
set -o errexit
set -o nounset

<<comment
This script cleans up an earlier load test. It reads from cleanup files that the load test script writes to
in order to determine which IDs to delete.
comment

echo "Sourcing environment variables from .env"
source .env

cd "$(dirname "$0")"
source load_test_utils.sh

function showhelp {
  echo -e """Usage $(dirname $0)/cleanup_load_test [OPTIONS]

  cleanup_load_test deletes resources that were created from an earlier load test.

  Available OPTIONs:

  ${CLEAR}-h
    ${GREEN}Display help

  ${CLEAR}-W <workspace id>
    ${GREEN}Specify the workspace ID from where connectors and connections should be deleted.
    Required.

  ${CLEAR}-H <hostname>
    ${GREEN}Specify the Airbyte API server hostname that the script should call to delete connectors and connections.
    Defaults to 'localhost'.

  ${CLEAR}-P <port>
    ${GREEN}Specify the port for the Airbyte server.
    Defaults to '8001'.

  ${CLEAR}-X <header>
    ${GREEN}Specify the X-Endpoint-API-UserInfo header value for API authentication.
    For Google Cloud Endpoint authentication only.
  """ && exit 1
}

hostname=localhost
api_port=8001
x_endpoint_header=""

while getopts "hW:H:P:X:kN:" options ; do
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
    X)
      x_endpoint_header="${OPTARG}"
      ;;
    *)
      showhelp
      ;;
  esac
done

function setup {
  if test -z "$workspace_id"; then
    echo "error: must set a workspace id with -W"
    exit 1
  fi

  echo "set workspace_id to ${workspace_id}"
  echo "set hostname to ${hostname}"
  echo "set api_port to ${api_port}"

  setCleanupFilesForWorkspace $workspace_id
}

function deleteConnections {
  while test -s $CONNECTION_CLEANUP_FILE
  do
    connectionId=$(readFirstLineFromFile $CONNECTION_CLEANUP_FILE)
    callApi "connections/delete" "{\"connectionId\":\"$connectionId\"}"
    echo "deleted connection with ID $connectionId"

    # deletion succeeded, so remove the ID from the cleanup file
    removeFirstLineFromFile $CONNECTION_CLEANUP_FILE
  done

  # if file exists and is empty
  if test -e $CONNECTION_CLEANUP_FILE && ! test -s $CONNECTION_CLEANUP_FILE
  then
    rm $CONNECTION_CLEANUP_FILE
    echo "removed cleanup file $CONNECTION_CLEANUP_FILE"
  fi
}

function deleteSources {
  while test -s $SOURCE_CLEANUP_FILE
  do
    sourceId=$(readFirstLineFromFile $SOURCE_CLEANUP_FILE)
    callApi "sources/delete" "{\"sourceId\":\"$sourceId\"}"
    echo "deleted source with ID $sourceId"

    # deletion succeeded, so remove the ID from the cleanup file
    removeFirstLineFromFile $SOURCE_CLEANUP_FILE
  done

  # if file exists and is empty
  if test -e $SOURCE_CLEANUP_FILE && ! test -s $SOURCE_CLEANUP_FILE
  then
    rm $SOURCE_CLEANUP_FILE
    echo "removed cleanup file $SOURCE_CLEANUP_FILE"
  fi
}

function deleteDestinations {
  while test -s $DESTINATION_CLEANUP_FILE
  do
    destinationId=$(readFirstLineFromFile $DESTINATION_CLEANUP_FILE)
    callApi "destinations/delete" "{\"destinationId\":\"$destinationId\"}"
    echo "deleted destination with ID $destinationId"

    # deletion succeeded, so remove the ID from the cleanup file
    removeFirstLineFromFile $DESTINATION_CLEANUP_FILE
  done

  # if file exists and is empty
  if test -e $DESTINATION_CLEANUP_FILE && ! test -s $DESTINATION_CLEANUP_FILE
  then
    rm $DESTINATION_CLEANUP_FILE
    echo "removed cleanup file $DESTINATION_CLEANUP_FILE"
  fi
}

############
##  MAIN  ##
############

if [[ $# -eq 0 ]] ; then
    showhelp
    exit 0
fi

setup

deleteConnections

deleteSources

deleteDestinations

echo "Finished!"
