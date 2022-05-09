#!/bin/bash
set -e

projectDir=( 
  "workers"
  "cli"
  "webapp"
  "server"
  "temporal"
  "container-orchestrator"
  "config/init"
  "bootloader"
  "metrics/reporter"
  "db/lib"
  "scheduler/app"
)

JDK_VERSION="17.0.1"
ALPINE_IMAGE="alpine:3.14"
POSTGRES_IMAGE="postgres:13-alpine"

for workdir in "${projectDir[@]}"
  do
    if [ $workdir = "metrics/reporter" ]; then
      artifactName="metrics-reporter" 
    else
      artifactName=${workdir%/*}
    fi
    docker buildx create --use --name $artifactName &&      \
    docker buildx build -t "airbyte/$artifactName:$VERSION" \
      --platform linux/amd64,linux/arm64                    \
      --build-arg VERSION=$VERSION                          \
      --build-arg ALPINE_IMAGE=$ALPINE_IMAGE                \
      --build-arg POSTGRES_IMAGE=$POSTGRES_IMAGE            \
      --build-arg JDK_VERSION=$JDK_VERSION                  \
      --push                                                \
      airbyte-$workdir/build/docker
    docker buildx rm $artifactName
done
