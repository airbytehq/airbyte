#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

assert_root

# Since KIND does not have access to the local docker agent, manually load the minimum images required for the Kubernetes Acceptance Tests.
# See https://kind.sigs.k8s.io/docs/user/quick-start/#loading-an-image-into-your-cluster.
echo "Loading images into KIND..."
kind load docker-image airbyte/server:dev --name chart-testing
kind load docker-image airbyte/scheduler:dev --name chart-testing
kind load docker-image airbyte/webapp:dev --name chart-testing
kind load docker-image airbyte/worker:dev --name chart-testing
kind load docker-image airbyte/db:dev --name chart-testing

echo "Starting app..."

echo "Applying dev-integration-test manifests to kubernetes..."
kubectl apply -k kube/overlays/dev-integration-test

echo "Waiting for server and scheduler to be ready..."
kubectl wait --for=condition=Available deployment/airbyte-server --timeout=300s || (kubectl describe pods && exit 1)
kubectl wait --for=condition=Available deployment/airbyte-scheduler --timeout=300s || (kubectl describe pods && exit 1)

echo "Checking if scheduler and server are being scheduled on separate nodes..."
if [ -n "$IS_MINIKUBE" ]; then
  SCHEDULER_NODE=$(kubectl get pod -o=custom-columns=NAME:.metadata.name,NODE:.spec.nodeName | grep scheduler | awk '{print $2}')
  SERVER_NODE=$(kubectl get pod -o=custom-columns=NAME:.metadata.name,NODE:.spec.nodeName | grep server | awk '{print $2}')

  if [ "$SCHEDULER_NODE" = "$SERVER_NODE" ]; then
    echo "Scheduler and server were scheduled on the same node! This should not be the case for testing!"
    exit 1
  else
    echo "Scheduler and server were scheduled on different nodes."
  fi
fi

echo "Listing nodes scheduled for pods..."
kubectl describe pods | grep "Name\|Node"

# allocates a lot of time to start kube. takes a while for postgres+temporal to work things out
sleep 120s

server_logs () { echo "server logs:" && kubectl logs deployment.apps/airbyte-server; }
scheduler_logs () { echo "scheduler logs:" && kubectl logs deployment.apps/airbyte-scheduler; }
pod_sweeper_logs () { echo "pod sweeper logs:" && kubectl logs deployment.apps/airbyte-pod-sweeper; }
describe_pods () { echo "describe pods:" && kubectl describe pods; }
print_all_logs () { server_logs; scheduler_logs; pod_sweeper_logs; describe_pods; }

trap "echo 'kube logs:' && print_all_logs" EXIT

kubectl port-forward svc/airbyte-server-svc 8001:8001 &

echo "Running worker integration tests..."
SUB_BUILD=PLATFORM  ./gradlew :airbyte-workers:integrationTest --scan

echo "Printing system disk usage..."
df -h

echo "Printing docker disk usage..."
docker system df

if [ -n "$CI" ]; then
  echo "Pruning all images..."
  docker image prune --all --force

  echo "Printing system disk usage after pruning..."
  df -h

  echo "Printing docker disk usage after pruning..."
  docker system df
fi

echo "Running e2e tests via gradle..."
KUBE=true SUB_BUILD=PLATFORM USE_EXTERNAL_DEPLOYMENT=true ./gradlew :airbyte-tests:acceptanceTests --scan
