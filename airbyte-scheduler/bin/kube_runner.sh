#!/usr/bin/env bash

set -e

JOB_ROOT=$1
echo "JOB_ROOT = $JOB_ROOT"

JOB_YAML_PATH=$2
echo "JOB_YAML_PATH = $JOB_YAML_PATH"

echo "Launch job..."
kubectl apply -f "$JOB_YAML_PATH"

JOB_NAME=$(grep airbyte-worker- < "$JOB_YAML_PATH" | cut -d " " -f4)
echo "JOB_NAME = $JOB_NAME"
JOB_UUID=$(kubectl get job "$JOB_NAME" -o "jsonpath={.metadata.labels.controller-uid}")
echo "JOB_UUID = $JOB_UUID"
POD_NAME=$(kubectl get po -l controller-uid="$JOB_UUID" -o name)
echo "POD_NAME = $POD_NAME"

JOB_ROOT_PARENT=$(dirname "$JOB_ROOT")

echo "Creating target directory..."
while ! (kubectl exec "$POD_NAME" -c worker-init -- mkdir -p "$JOB_ROOT_PARENT")
do
  sleep 1
  echo "Retrying..."
done

echo "Copying config files..."
UNQUALIFIED_POD_NAME=$(basename "$POD_NAME") # kubectl cp doesn't work with the pod/ prefix
while ! (kubectl cp "$JOB_ROOT" "$UNQUALIFIED_POD_NAME":"$JOB_ROOT_PARENT" -c worker-init)
do
  sleep 1
  echo "Retrying..."
done

echo "Listing copied files..."
kubectl exec "$POD_NAME" -c worker-init -- find "$JOB_ROOT"

echo "Creating /ready file to indicate the container can start..."
kubectl exec "$POD_NAME" -c worker-init -- touch "$JOB_ROOT/ready"

echo "Waiting for pod to start and emitting logs..."
while ! (kubectl logs "$POD_NAME" --follow --pod-running-timeout=1000m)
do
  sleep 1
  echo "Retrying..."
done

PHASE=$(kubectl get "$POD_NAME" --output="jsonpath={.status.phase}")
echo "Phase of pod: $PHASE"

if [[ "$PHASE" == "Failed" ]]; then
  echo "Failed: Exiting with code 1"
  exit 1
elif [[ "$PHASE" == "Unknown" ]]; then
  echo "Unknown: Exiting with code 1"
  exit 1
else
  echo "Success: Exiting code 0"
  exit 0
fi
