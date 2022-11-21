export DOCKER_BUILD_PLATFORM=linux/amd64
export ALPINE_IMAGE=amd64/alpine:3.14
export DOCKER_BUILD_ARCH=amd64
./tools/bin/setup_connector_venv.sh $1 python3.9
./gradlew :airbyte-integrations:connectors:$1:build && docker tag docker.io/airbyte/$1:dev ghcr.io/estuary/$1:local
