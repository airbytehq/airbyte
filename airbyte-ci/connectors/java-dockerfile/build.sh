set -e

CONNECTOR_PATH="airbyte-integrations/connectors/source-mysql"
CONNECTOR_NAME="source-mysql"
IMAGE_TAG="dev"

while [[ $# -gt 0 ]]; do
  case $1 in
    --connector)
      CONNECTOR_PATH="airbyte-integrations/connectors/$2"
      CONNECTOR_NAME="$2"
      shift 2
      ;;
    --tag)
      IMAGE_TAG="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--connector CONNECTOR_NAME] [--tag TAG]"
      exit 1
      ;;
  esac
done

if [ ! -d "../../../$CONNECTOR_PATH" ]; then
  echo "Error: Connector directory not found: $CONNECTOR_PATH"
  exit 1
fi

echo "Building Docker image for $CONNECTOR_NAME..."
docker build \
  --build-arg CONNECTOR_PATH="$CONNECTOR_PATH" \
  --build-arg CONNECTOR_NAME="$CONNECTOR_NAME" \
  -t "airbyte/$CONNECTOR_NAME:$IMAGE_TAG" \
  -f Dockerfile \
  ../../../

echo "Image built successfully: airbyte/$CONNECTOR_NAME:$IMAGE_TAG"
