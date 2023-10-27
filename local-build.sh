_push=0
while getopts ":hp" option; do
   case $option in
      h) # display Help
         echo "Build a connector image locally."
         echo "local-build.sh [OPTIONS] <connector-name>"
         echo ""
         echo "Options:"
         echo "-p   publish the image to ghcr, namespace with your username or codespace name"
         exit;;
      p)
        _push=1
   esac
done

connector=${@:$OPTIND:1}

export DOCKER_BUILD_PLATFORM=linux/amd64
export ALPINE_IMAGE=amd64/alpine:3.14
export DOCKER_BUILD_ARCH=amd64

if [ -f "airbyte-integrations/connectors/$connector/requirements.txt" ]; then
   ./tools/bin/setup_connector_venv.sh $connector python3.9
    export AIRBYTE_TO_FLOW_TAG="dev"
   ./gradlew :airbyte-integrations:connectors:$connector:airbyteDocker
   docker tag docker.io/airbyte/$connector:dev ghcr.io/estuary/$connector:local
else
   docker build airbyte-integrations/connectors/$connector -f airbyte-integrations/connectors/$connector/Dockerfile -t ghcr.io/estuary/$connector:local
fi

if [[ "$_push" -eq "1" ]]; then
    tag=$CODESPACE_NAME
    if [[ -z "$tag" ]]; then
        tag="$USER-airbyte"
    fi
    docker tag docker.io/airbyte/$connector:dev ghcr.io/estuary/$connector:$tag
    docker push ghcr.io/estuary/$connector:$tag
fi
