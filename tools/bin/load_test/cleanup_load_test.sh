#!/usr/bin/env bash

<<comment
This script cleans up an earlier load test. It reads from cleanup files that the load test script writes to
in order to determine which IDs to delete.
comment

cd "$(dirname "$0")"
. load_test_utils.sh

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CLEAR='\033[0m'

function showhelp {
  echo -e """Usage $(dirname $0)/cleanup_load_test [OPTIONS]

  cleanup_load_test deletes resources that were created from an earlier load test.

  Available OPTIONs:

  ${CLEAR}-h
    ${GREEN}Display help

  ${CLEAR}-W <workspace id>
    ${GREEN}Specify the workspace ID from where connectors and connections should be deleted

  ${CLEAR}-H <hostname>
    ${GREEN}Specify the Airbyte API server hostname that the script should call to delete connectors and connections.
    Defaults to 'localhost'.

  ${CLEAR}-P <port>
    ${GREEN}Specify the port for the Airbyte server. If kube (ie. '-k' is provided), port-forwarding
    will be set up for the airbyte-server deployment using the provided <port> (ie. '8001:8001').
    Defaults to '8001'.

  ${CLEAR}-k
    ${GREEN}Indicate that the script is running against a kubernetes instance of Airbyte

  ${CLEAR}-N <namespace>
    ${GREEN}Specify the kubernetes namespace where the airbyte-server deployment exists g (ex. "ab").
    Only use with '-k' option.
    Defaults to 'default'.
  """ && exit 1
}

hostname=localhost
api_port=8001
kube=false
kube_namespace=default

while getopts "hW:H:P:kN:" options ; do
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

function setup {
  if test -z "$workspace_id"; then
    echo "error: must set a workspace id with -W"
    exit 1
  fi

  echo "set workspace_id to ${workspace_id}"
  echo "set hostname to ${hostname}"
  echo "set api_port to ${api_port}"
  echo "set kube to ${kube}"
  echo "set kube_namespace to ${kube_namespace}"

  setCleanupFilesForWorkspace $workspace_id
}

function callApi {
  # call the API with the endpoint passed as arg $1, and (optional) payload passed as arg $2
  # example of calling the API with a payload:
  #    callApi "destinations/list" "{\"workspaceId\":\"${workspace}\"}"

  curl -s -X POST -H 'Content-Type: application/json' -H "X-Endpoint-API-UserInfo: ${api_header}" -d "$2" "${hostname}:${api_port}/api/v1/$1"
}

function portForward {
  # if running against kubernetes, set up "kubectl port-forward airbyte-server 8001:8001 -n ab" or something similar
  # note that local kube doesn't run in the ab namespace, so that should be optional
  echo "implement me"
}

function deleteConnections {
  while test -s $connection_cleanup_file
  do
    connectionId=$(readFirstLineFromFile $connection_cleanup_file)
    callApi "connections/delete" "{\"connectionId\":\"$connectionId\"}"
    echo "deleted connection with ID $connectionId"

    # deletion succeeded, so remove the ID from the cleanup file
    removeFirstLineFromFile $connection_cleanup_file
  done

  if ! test -s $connection_cleanup_file
  then
    rm $connection_cleanup_file
    echo "removed cleanup file $connection_cleanup_file"
  fi
}

function deleteSources {
  while test -s $source_cleanup_file
  do
    sourceId=$(readFirstLineFromFile $source_cleanup_file)
    callApi "sources/delete" "{\"sourceId\":\"$sourceId\"}"
    echo "deleted source with ID $sourceId"

    # deletion succeeded, so remove the ID from the cleanup file
    removeFirstLineFromFile $source_cleanup_file
  done

  if ! test -s $source_cleanup_file
  then
    rm $source_cleanup_file
    echo "removed cleanup file $source_cleanup_file"
  fi
}

function deleteDestinations {
  while test -s $destination_cleanup_file
  do
    destinationId=$(readFirstLineFromFile $destination_cleanup_file)
    callApi "destinations/delete" "{\"destinationId\":\"$destinationId\"}"
    echo "deleted destination with ID $destinationId"

    # deletion succeeded, so remove the ID from the cleanup file
    removeFirstLineFromFile $destination_cleanup_file
  done

  if ! test -s $destination_cleanup_file
  then
    rm $destination_cleanup_file
    echo "removed cleanup file $destination_cleanup_file"
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
