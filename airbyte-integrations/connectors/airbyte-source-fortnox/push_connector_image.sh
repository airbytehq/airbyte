#!/usr/bin/env bash

TAG=dev
LOCAL_IMAGE=airbyte/source-fortnox:$TAG
ARTIFACT_REGISTRY=europe-west1-docker.pkg.dev/ark-kapital-production/airbyte-artifact-registry
REMOTE_IMAGE=$ARTIFACT_REGISTRY/$LOCAL_IMAGE

echo "Building $LOCAL_IMAGE image..."
docker buildx build --platform linux/amd64 -t $LOCAL_IMAGE .

echo "Tagging image $LOCAL_IMAGE -> $REMOTE_IMAGE..."
docker tag $LOCAL_IMAGE $REMOTE_IMAGE

echo "Pushing image..."
docker push $REMOTE_IMAGE

echo "Pulling image within Airbyte..."
gcloud compute ssh airbyte-production --project=ark-kapital-production --command="docker pull $REMOTE_IMAGE"
