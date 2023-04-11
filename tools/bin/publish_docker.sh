#!/bin/bash
set -e

# todo (cgardens) - remove this file. used in platform build script only.
# List of directories without "airbyte-" prefix.
projectDir=(
  "bootloader"
  "container-orchestrator"
  "cron"
  "connector-builder-server"
  "metrics/reporter"
  "proxy"
  "server"
  "temporal"
  "webapp"
  "workers"
)

# Set default values to required vars. If set in env, values will be taken from there.
# Primarily for testing.
JDK_VERSION=${JDK_VERSION:-17.0.4}
ALPINE_IMAGE=${ALPINE_IMAGE:-alpine:3.14}
POSTGRES_IMAGE=${POSTGRES_IMAGE:-postgres:13-alpine}

# Iterate over all directories in list to build one by one.
# metrics-reporter are exception due to wrong artifact naming
for workdir in "${projectDir[@]}"
  do
    case $workdir in
      "metrics/reporter")
        artifactName="metrics-reporter"
        ;;

      "config/init")
        artifactName="init"
        ;;

      "workers")
        artifactName="worker"
        ;;

      *)
        artifactName=${workdir%/*}
        ;;
    esac

    echo "Publishing airbyte/$artifactName..."
    sleep 1

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
