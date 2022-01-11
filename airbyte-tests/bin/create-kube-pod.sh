#!/usr/bin/env bash

create_only=0
delete=1
total_num_pods=100
while getopts 'c:kh' opt; do
  case "$opt" in
    c)
      echo "Running in create-only mode.."
      create_only=1
      total_num_pods=$OPTARG
      ;;
    k)
      echo "Will not delete completed pods.."
      delete=0
      ;;
    ?|h)
      echo "Usage: $(basename $0) [-c] [-k]"
      exit 1
      ;;
  esac
done
shift "$(($OPTIND -1))"


if [ $create_only -eq 0 ]
then
  # watch api and pipe to file
  echo "Watching for events.."
  curl -sN http://127.0.0.1:8001/api/v1/namespaces/default/pods\?watch\=1 | \
    jq -c 'select(.object.status.phase == "Running") | { "name": .object.metadata.name, "namespace": .object.metadata.namespace, "creationTimestamp": .object.metadata.creationTimestamp, "phase": .object.status.phase, "conditions": [ .object.status.conditions | .[] | select(.status == "True") | {(.type): .lastTransitionTime} ] | add } | select(.conditions.Ready)' >> ./data-local-100-completed.txt &
fi

echo "Creating $total_num_pods test pods.."
i=1
while [ $i -ne "$total_num_pods" ]
do
  echo "creating pod number: $i"
  kubectl create -f ./test-pod.yaml

  if [ $create_only -eq 0 ]
  then
      # wait till pod is in complete; this works well if there is only one pod
      while [[ "$(kubectl get pod | grep -c "Running")" -eq 1 ]] || [[ "$(kubectl get pod | grep -c "Pending")" -eq 1 ]] || [[ "$(kubectl get pod | grep -c "ContainerCreating")" -eq 1 ]]
      do
        echo 'wait for pod to finish..'
        sleep 2
      done

      # remove old pod to not mess with results;
      if [ $delete -eq 1 ]
      then
        kubectl get pod | grep Comp | awk '{print $1}' | xargs kubectl delete pod
      fi

      # sleep to let Kube cluster rest
      sleep 2;

  fi
  i=$((i+1))
done
