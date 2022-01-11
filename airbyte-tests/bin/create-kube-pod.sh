#!/usr/bin/env bash

create_only=0

while getopts 'c:h' opt; do
  case "$opt" in
    a)
      echo "Running in create-only mode.."
      create_only=1
      ;;

    ?|h)
      echo "Usage: $(basename $0) [-c]"
      exit 1
      ;;
  esac
done
shift "$(($OPTIND -1))"

# watch api and pipe to file
curl -sN http://127.0.0.1:8001/api/v1/namespaces/default/pods\?watch\=1 | \
  jq -c 'select(.object.status.phase == "Running") | { "name": .object.metadata.name, "namespace": .object.metadata.namespace, "creationTimestamp": .object.metadata.creationTimestamp, "phase": .object.status.phase, "conditions": [ .object.status.conditions | .[] | select(.status == "True") | {(.type): .lastTransitionTime} ] | add } | select(.conditions.Ready)' >> ./data-gke-1.21.txt &


i=1
while [ $i -ne 300 ]
do
  echo "creating pod number: $i"
  kubectl create -f ./test-pod.yaml

  if [ $create_only -eq 0 ]
  then
      echo "running in clean up mode.."
      
      # wait till pod is in complete
      while [ "$(kubectl get pod | grep -c 'Compl')" -eq 0 ]
      do
        echo 'wait for pod to finish..'
        sleep 2
      done

      # remove old pod to not mess with results; sleep to let Kube cluster rest
      kubectl get pod | grep Comp | awk '{print $1}' | xargs kubectl delete pod
      sleep 1;

  fi
  i=$((i+1))
done
