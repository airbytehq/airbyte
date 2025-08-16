#!/usr/bin/env bash
set -euo pipefail

#
# Upload Python connector dependencies metadata to GCS
# Extracted from airbyte-ci publish pipeline for GitHub Actions integration
#
# Usage: ./poe-tasks/upload-python-depdendencies.sh --name source-avri [--pre-release] [--main-release]
#

# source utility functions
source "${BASH_SOURCE%/*}/lib/util.sh"

function usage() {
    cat << EOF
Usage: $0 [options]

Upload Python connector dependencies metadata to GCS.

Must be run from the root of the airbyte repo

Options:
    -n, --name CONNECTOR_NAME     Connector name (required)
    --bucket BUCKET_NAME          GCS bucket name (optional, defaults to dev bucket)
    --connector-version VERSION   Connector version (optional, default reads from metadata.yaml)
    --pre-release                 Publish as a pre-release (uses a dev version derived from the current timestamp)
    -h, --help                    Show this help message

Environment Variables:
    GCS_CREDENTIALS              JSON-formatted GCP service account key set as an environment variable (required)

Examples:
    $0 --name source-avni
    $0 --name source-avni --bucket my-test-bucket --version dev.1.2.3
EOF
}

# Default values
BUCKET_NAME="dev-airbyte-cloud-connector-metadata-service"
CONNECTOR_NAME=""
VERSION=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--name)
            CONNECTOR_NAME="$2"
            shift 2
            ;;
        --bucket)
            BUCKET_NAME="$2"
            shift 2
            ;;
        --connector-version)
            VERSION="$2"
            shift 2
            ;;
        --pre-release)
            PRE_RELEASE=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage >&2
            exit 1
            ;;
    esac
done

# Validate required parameters
if [[ -z "$CONNECTOR_NAME" ]]; then
    echo "Error: Connector name is required" >&2
    usage >&2
    exit 1
fi

# Use environment variables as fallback
if [[ -z "$BUCKET_NAME" ]]; then
    echo "Error: GCS bucket name is required" >&2
    exit 1
fi

if ! test "$GCS_CREDENTIALS"; then
  echo "GCS_CREDENTIALS environment variable must be set" >&2
  exit 1
fi

# Navigate to connector directory
CONNECTOR_DIR="airbyte-integrations/connectors/$CONNECTOR_NAME"
if [[ ! -d "$CONNECTOR_DIR" ]]; then
    echo "Error: Connector directory not found: $CONNECTOR_DIR" >&2
    exit 1
fi

cd "$CONNECTOR_DIR"

# Check if this is a Python connector
CONNECTOR_LANGUAGE=$(poe -qq get-language)
if [[ "$CONNECTOR_LANGUAGE" != "python" ]]; then
    echo "⚠️ Connector language is '$CONNECTOR_LANGUAGE', not Python. Skipping dependencies upload."
    exit 0
fi

# Resolve the connector version
if [[ -z "$VERSION" ]]; then
    VERSION=$(poe -qq get-version)
fi
if [[ $PRE_RELEASE == true ]]; then
    VERSION=$(generate_dev_tag "$VERSION")
fi

echo "Uploading dependencies for connector: $CONNECTOR_NAME"
echo "  Version: $VERSION"
echo "  GCS Bucket: $BUCKET_NAME"

DOCKER_REPOSITORY=$(yq eval '.data.dockerRepository' metadata.yaml)
DEFINITION_ID=$(yq eval '.data.definitionId' metadata.yaml)

# Authenticate with GCS
gcloud_activate_service_account "$GCS_CREDENTIALS"

# Install the connector and get dependencies
if ! [[ -f "pyproject.toml" ]]; then
    echo "⚠️ No pyproject.toml found, skipping dependency upload" >&2
    exit 0
fi

echo "Installing Poetry dependencies..."
# Export dependencies from poetry using pip list
poetry install --all-extras
DEPENDENCIES_JSON=$(poetry run pip freeze | jq -R -s -c 'split("\n")[:-1] | map(select(contains("=="))) | map({package_name: split("==")[0], version: split("==")[1]})')
GENERATION_TIME=$(date -u +"%Y-%m-%dT%H:%M:%S.%N")

METADATA_JSON=$(cat << EOF
{
    "connector_technical_name": "$CONNECTOR_NAME",
    "connector_repository": "$DOCKER_REPOSITORY",
    "connector_version": "$VERSION",
    "connector_definition_id": "$DEFINITION_ID",
    "dependencies": $DEPENDENCIES_JSON,
    "generation_time": "$GENERATION_TIME"
}
EOF
)

# Create temporary file for upload
TEMP_FILE=$(mktemp)
echo "$METADATA_JSON" > "$TEMP_FILE"

# Upload to GCS
GCS_KEY="connector_dependencies/${CONNECTOR_NAME}/${VERSION}/dependencies.json"
echo "Uploading to: gs://${BUCKET_NAME}/${GCS_KEY}"

gsutil cp "$TEMP_FILE" "gs://${BUCKET_NAME}/${GCS_KEY}"

echo "Successfully uploaded dependencies metadata for $CONNECTOR_NAME ($VERSION)"