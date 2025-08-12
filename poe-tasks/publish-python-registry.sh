#!/bin/bash
#
# Publish a Python connector to PyPI registry
# Extracted from airbyte-ci publish pipeline for GitHub Actions integration
#

set -euo pipefail

function usage() {
    cat << EOF
Usage: $0 [options]

Publish a Python connector to PyPI registry.

Options:
    -n, --name CONNECTOR_NAME     Connector name (required)
    -t, --token TOKEN             PyPI token (required)
    -v, --version VERSION        Override version (optional)
    --pre-release                publish as a pre-release (uses a dev version derived from the current timestamp)
    -h, --help                   Show this help message

Environment Variables:
    PYTHON_REGISTRY_TOKEN        PyPI token (alternative to --token)

Examples:
    $0 --name source-faker --token \$PYPI_TOKEN
    $0 --name source-faker --token \$PYPI_TOKEN --pre-release
EOF
}

function should_publish_pypi() {
    # Check if the connector is enabled for PyPI publishing
    if yq eval '.data.remoteRegistries.pypi.enabled' ${POE_PWD}/metadata.yaml 2>/dev/null | grep -q 'true'; then
        return 0
    else
        return 1
    fi
}

function get_pypi_package_name() {
    # Extract the package name from metadata.yaml
    yq eval '.data.remoteRegistries.pypi.packageName' ${POE_PWD}/metadata.yaml
}

# Default values
REGISTRY_URL="https://upload.pypi.org/legacy/"
PRE_RELEASE=false
CONNECTOR_NAME=""
PYPI_TOKEN=""
VERSION_OVERRIDE=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--name)
            CONNECTOR_NAME="$2"
            shift 2
            ;;
        -t|--token)
            PYPI_TOKEN="$2"
            shift 2
            ;;
        -v|--version)
            VERSION_OVERRIDE="$2"
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
if [[ -z "$PYPI_TOKEN" && -n "${PYTHON_REGISTRY_TOKEN:-}" ]]; then
    PYPI_TOKEN="$PYTHON_REGISTRY_TOKEN"
fi

if [[ -z "$PYPI_TOKEN" ]]; then
    echo "Error: PyPI token is required (use --token or set PYTHON_REGISTRY_TOKEN in your environment)" >&2
    exit 1
fi


# Navigate to connector directory
CONNECTOR_DIR="airbyte-integrations/connectors/$CONNECTOR_NAME"
if [[ ! -d "$CONNECTOR_DIR" ]]; then
    echo "Error: Connector directory not found: $CONNECTOR_DIR" >&2
    exit 1
fi

cd "$CONNECTOR_DIR"

echo "Publishing connector: $CONNECTOR_NAME"
echo "Registry URL: $REGISTRY_URL"

# Check if PyPI publishing is enabled in metadata
if ! should_publish; then
    echo "PyPI publishing is not enabled for this connector. Skipping."
    exit 0
fi

# Get package metadata from metadata.yaml
PACKAGE_NAME=$(get_pypi_package_name)
if [[ -z "$PACKAGE_NAME" ]]; then
    echo "Error: Package name not found in metadata.yaml" >&2
    exit 1
fi
BASE_VERSION=$(poe -qq get-version)

# Determine version to use
if [[ -n "$VERSION_OVERRIDE" ]]; then
    VERSION="$VERSION_OVERRIDE"
elif [[ "$PRE_RELEASE" == "true" ]]; then
    # Add current timestamp for pre-release.
    # we can't use the git revision because not all python registries allow local version identifiers. 
    # Public version identifiers must conform to PEP 440 and only allow digits.
    TIMESTAMP=$(date +"%Y%m%d%H%M")
    VERSION="${BASE_VERSION}.dev${TIMESTAMP}"
else
    VERSION="$BASE_VERSION"
fi

echo "Package name: $PACKAGE_NAME"
echo "Version: $VERSION"

# Check if package already exists
CHECK_URL="https://pypi.org/pypi"

# Simple check for existing package
if [[ $(curl -s -o /dev/null -w "%{http_code}" "$CHECK_URL/$PACKAGE_NAME/$VERSION/json") == "200" ]]; then
    echo "Package $PACKAGE_NAME version $VERSION already exists. Skipping."
    exit 0
fi

# Assumes the connector uses Poetry for packaging and has a pyproject.toml
if [[ -f "pyproject.toml" ]]; then
    echo "Detected Poetry project"
    
    # Install dependencies
    poetry install --all-extras
    
    # Configure and publish with Poetry
    poetry config repositories.mypypi "$REGISTRY_URL"
    poetry config pypi-token.mypypi "$PYPI_TOKEN"
    poetry config requests.timeout 60
    
    poetry publish --build --repository mypypi --no-interaction -vvv
    
else
    echo "Error: No pyproject.toml, skipping publishing to PyPI" >&2
    exit 0
fi

echo "Successfully published $PACKAGE_NAME version $VERSION to PyPI"