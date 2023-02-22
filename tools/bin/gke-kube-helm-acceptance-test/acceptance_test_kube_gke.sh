#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

assert_root
kubectl --help

NAMESPACE=$(openssl rand -hex 12)
echo "Namespace" $NAMESPACE

TAG=$(openssl rand -hex 12)
echo "Tag" $TAG

docker login -u "$DOCKER_HUB_USERNAME" -p "$DOCKER_HUB_PASSWORD"
VERSION=$TAG ./gradlew build
# VERSION=$TAG docker compose -f docker-compose.build.yaml push

# For running on Mac
#sed -i .bak 's/default/'$NAMESPACE'/g' kube/overlays/dev/kustomization.yaml
#sed -i .bak 's/dev/'$TAG'/g' kube/overlays/dev/kustomization.yaml

# sed -i 's/default/'$NAMESPACE'/g' kube/overlays/dev/kustomization.yaml
# sed -i 's/dev/'$TAG'/g' kube/overlays/dev/kustomization.yaml

helm upgrade --install --debug --namespace $NAMESPACE \\
--set airbyte-bootloader.image.tag=$TAG \\
--set webapp.image.tag=$TAG \\
--set worker.image.tag=$TAG \\
--set server.image.tag=$TAG \\
 ab charts/airbyte
kubectl apply -f tools/bin/gke-kube-helm-acceptance-test/postgres-source.yaml --namespace=$NAMESPACE
kubectl apply -f tools/bin/gke-kube-helm-acceptance-test/postgres-destination.yaml --namespace=$NAMESPACE

sleep 180s

function findAndDeleteTag () {
    if [ $(curl --fail -LI --request GET 'https://hub.docker.com/v2/repositories/airbyte/'$1'/tags/'$TAG'/' --header 'Authorization: JWT '$2'' -o /dev/null -w '%{http_code}\n' -s) == "200" ];
    then
        echo "FOUND TAG" $TAG "in repository" $1 ",DELETING IT"
        curl --request DELETE 'https://hub.docker.com/v2/repositories/airbyte/'$1'/tags/'$TAG'/' --header 'Authorization: JWT '$2'';
    else
      echo "NOT FOUND TAG" $TAG "in repository" $1;
    fi
}

function cleanUpImages () {
    TOKEN=$(curl --request POST 'https://hub.docker.com/v2/users/login/' --header 'Content-Type: application/json' --data-raw '{"username":"'$DOCKER_HUB_USERNAME'","password":"'$DOCKER_HUB_PASSWORD'"}' | jq '.token')
    TOKEN="${TOKEN%\"}"
    TOKEN="${TOKEN#\"}"

    findAndDeleteTag "init" $TOKEN
    findAndDeleteTag "db" $TOKEN
    findAndDeleteTag "seed" $TOKEN
    findAndDeleteTag "scheduler" $TOKEN
    findAndDeleteTag "server" $TOKEN
    findAndDeleteTag "webapp" $TOKEN
    findAndDeleteTag "migration" $TOKEN
    findAndDeleteTag "cron" $TOKEN
}

trap "kubectl delete namespaces $NAMESPACE --grace-period=0 --force" EXIT

kubectl port-forward svc/airbyte-server-svc 8001:8001 --namespace=$NAMESPACE &

kubectl port-forward svc/postgres-source-svc 2000:5432 --namespace=$NAMESPACE &

kubectl port-forward svc/postgres-destination-svc 4000:5432 --namespace=$NAMESPACE &

sleep 10s

echo "Running e2e tests via gradle..."
KUBE=true IS_GKE=true SUB_BUILD=PLATFORM USE_EXTERNAL_DEPLOYMENT=true ./gradlew :airbyte-tests:acceptanceTests --scan -i

