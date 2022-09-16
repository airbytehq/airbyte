#!/usr/bin/env bash

# ------------- Import some defaults for the shell

# Source shell defaults
# $0 is the currently running program (this file)
this_file_directory=$(dirname $0)
relative_path_to_defaults=$this_file_directory/../shell_defaults

. tools/lib/lib.sh

assert_root

# Since KIND does not have access to the local docker agent, manually load the minimum images required for the Kubernetes Acceptance Tests.
# See https://kind.sigs.k8s.io/docs/user/quick-start/#loading-an-image-into-your-cluster.
if [ -n "$CI" ]; then
  mkdir -p kind_logs
  echo -e "$blue_text""Loading images into KIND...""$default_text"
  kind load docker-image airbyte/server:dev --name chart-testing > kind_logs/server &
  process_ids=$!
  kind load docker-image airbyte/webapp:dev --name chart-testing > kind_logs/webapp &
  process_ids="$! $process_ids"
  kind load docker-image airbyte/worker:dev --name chart-testing > kind_logs/worker &
  process_ids="$! $process_ids"
  kind load docker-image airbyte/db:dev --name chart-testing > kind_logs/db &
  process_ids="$! $process_ids"
  kind load docker-image airbyte/container-orchestrator:dev --name chart-testing > kind_logs/container &
  process_ids="$! $process_ids"
  kind load docker-image airbyte/bootloader:dev --name chart-testing > kind_logs/bootloader &
  kind load docker-image airbyte/cron:dev --name chart-testing > kind_logs/cron &
  process_ids="$! $process_ids"
  tail -f kind_logs/* &
  tail_id=$!
  echo -e "$blue_text""Waiting for the following process IDs to finish $process_ids""$default_text"
  wait $process_ids && kill $tail_id
fi

echo -e "$blue_text""Starting app...""$default_text"

echo -e "$blue_text""Applying dev-integration-test manifests to kubernetes...""$default_text"
kubectl apply -k kube/overlays/dev-integration-test

echo -e "$blue_text""Waiting for server to be ready...""$default_text"
kubectl wait --for=condition=Available deployment/airbyte-server --timeout=300s || (kubectl describe pods && exit 1)

echo -e "$blue_text""Listing nodes scheduled for pods...""$default_text"
kubectl describe pods | grep "Name\|Node"

# allocates a lot of time to start kube. takes a while for postgres+temporal to work things out
echo -e "$blue_text""Sleeping 120 seconds""$default_text"
sleep 120s

if [ -n "$CI" ]; then
  server_logs () { kubectl logs deployment.apps/airbyte-server > /tmp/kubernetes_logs/server.txt; }
  pod_sweeper_logs () { kubectl logs deployment.apps/airbyte-pod-sweeper > /tmp/kubernetes_logs/pod_sweeper.txt; }
  worker_logs () { kubectl logs deployment.apps/airbyte-worker > /tmp/kubernetes_logs/worker.txt; }
  db_logs () { kubectl logs deployment.apps/airbyte-db > /tmp/kubernetes_logs/db.txt; }
  temporal_logs () { kubectl logs deployment.apps/airbyte-temporal > /tmp/kubernetes_logs/temporal.txt; }
  describe_pods () { kubectl describe pods > /tmp/kubernetes_logs/describe_pods.txt; }
  describe_nodes () { kubectl describe nodes > /tmp/kubernetes_logs/describe_nodes.txt; }
  write_all_logs () {
    server_logs;
    worker_logs;
    db_logs;
    temporal_logs;
    pod_sweeper_logs;
    describe_nodes;
    describe_pods;
  }
# Uncomment for debugging. Warning, this is verbose.
#  trap "mkdir -p /tmp/kubernetes_logs && write_all_logs" EXIT
fi

kubectl port-forward svc/airbyte-server-svc 8001:8001 > /tmp/kubernetes_logs/port_forward_command.txt &
process_ids=$!
tail -f kind_logs/* &
tail_id=$!
echo -e "$blue_text""Waiting for the following process IDs to finish $process_ids""$default_text"
wait -$process_ids && kill $tail_id


echo -e "$blue_text""Running worker integration tests...""$default_text"
SUB_BUILD=PLATFORM  ./gradlew :airbyte-workers:integrationTest --scan

echo -e "$blue_text""Printing system disk usage...""$default_text"
df -h

echo -e "$blue_text""Printing docker disk usage...""$default_text"
docker system df

if [ -n "$CI" ]; then
  echo -e "$blue_text""Pruning all images...""$default_text"
  docker image prune --all --force

  echo -e "$blue_text""Printing system disk usage after pruning...""$default_text"
  df -h

  echo -e "$blue_text""Printing docker disk usage after pruning...""$default_text"
  docker system df
fi

echo -e "$blue_text""Running e2e tests via gradle...""$default_text"
KUBE=true SUB_BUILD=PLATFORM USE_EXTERNAL_DEPLOYMENT=true ./gradlew :airbyte-tests:acceptanceTests --scan

echo -e "$blue_text""Listing still running jobs! If you see any they thing won't end""$default_text"
jobs
kill $(jobs -p)
rm -rf kind_logs
echo -e "$blue_text""If you are reading the the script has completed without error""$default_text"
