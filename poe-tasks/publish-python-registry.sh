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

Must be run from the root of the Airbyte repository with Poetry installed

Options:
    -n, --name CONNECTOR_NAME     Connector name (required)
    -t, --token TOKEN             PyPI token (optional, specify this or set PYTHON_REGISTRY_TOKEN environment variable)
    -v, --version VERSION         Override version (optional)
    --release-type TYPE           Release type (optional): 'pre-release' or 'main-release' (default is 'pre-release')
    --test-registry               Use the test PyPI registry (default is production registry)
    -h, --help                    Show this help message

Environment Variables:
    PYTHON_REGISTRY_TOKEN        PyPI token (alternative to --token)

Examples:
    $0 --name source-faker --token \$PYPI_TOKEN
    $0 --name source-faker --token \$PYPI_TOKEN --release-type main-release
EOF
}

should_publish_pypi() {
    # Check if the connector is enabled for PyPI publishing
    if yq eval '.data.remoteRegistries.pypi.enabled' "$1" 2>/dev/null | grep -q 'true'; then
        return 0
    else
        return 1
    fi
}

function get_pypi_package_name() {
    # Extract the package name from metadata.yaml
    yq eval '.data.remoteRegistries.pypi.packageName' "$1"
}

# Default values
REGISTRY_UPLOAD_URL="https://upload.pypi.org/legacy/"
REGISTRY_CHECK_URL="https://pypi.org/pypi"
REGISTRY_PACKAGE_URL="https://pypi.org/project"

TEST_REGISTRY_UPLOAD_URL="https://test.pypi.org/legacy/"
TEST_REGISTRY_CHECK_URL="https://test.pypi.org/pypi"
TEST_REGISTRY_PACKAGE_URL="https://test.pypi.org/project"

RELEASE_TYPE="pre-release"
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
        --release-type)
            RELEASE_TYPE="$2"
            shift 2
            ;;
        --test-registry)
            REGISTRY_UPLOAD_URL="$TEST_REGISTRY_UPLOAD_URL"
            REGISTRY_CHECK_URL="$TEST_REGISTRY_CHECK_URL"
            REGISTRY_PACKAGE_URL="$TEST_REGISTRY_PACKAGE_URL"
            echo "🧪 Using Test PyPI registry: $REGISTRY_UPLOAD_URL"
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

if [[ "$RELEASE_TYPE" != "pre-release" && "$RELEASE_TYPE" != "main-release" ]]; then
    echo "Error: Invalid release type '$RELEASE_TYPE'. Valid options are 'pre-release' or 'main-release'." >&2
    usage >&2
    exit 1
fi
    
# Use environment variables as fallback
if [[ -z "$PYPI_TOKEN" && -n "${PYTHON_REGISTRY_TOKEN:-}" ]]; then
    PYPI_TOKEN="$PYTHON_REGISTRY_TOKEN"
fi

if [[ -z "$PYPI_TOKEN" ]]; then
    echo "Error: PyPI token is required (use --token or set PYTHON_REGISTRY_TOKEN in your environment), skipping PyPI publishing" >&2
    exit 0
fi


# Navigate to connector directory
CONNECTOR_DIR="airbyte-integrations/connectors/$CONNECTOR_NAME"
if [[ ! -d "$CONNECTOR_DIR" ]]; then
    echo "Error: Connector directory not found: $CONNECTOR_DIR" >&2
    exit 1
fi

cd "$CONNECTOR_DIR"

METADATA_FILE="metadata.yaml"
if [[ ! -f "$METADATA_FILE" ]]; then
    echo "Error: metadata.yaml not found in $CONNECTOR_DIR" >&2
    exit 1
fi

echo "Publishing connector: $CONNECTOR_NAME"
echo "Registry URL: $REGISTRY_UPLOAD_URL"

# Check if PyPI publishing is enabled in metadata
if ! should_publish_pypi "$METADATA_FILE"; then
    echo "✅ PyPI publishing is not enabled for this connector, skipping PyPI publishing."
    exit 0
fi

# Get package metadata from metadata.yaml
PACKAGE_NAME=$(get_pypi_package_name "$METADATA_FILE")
if [[ -z "$PACKAGE_NAME" ]]; then
    echo "⚠️ Error: Package name not found in metadata.yaml, skipping PyPI publishing." >&2
    exit 0
fi
BASE_VERSION=$(poe -qq get-version)

# Determine version to use
if [[ -n "$VERSION_OVERRIDE" ]]; then
    VERSION="$VERSION_OVERRIDE"
elif [[ "$RELEASE_TYPE" == "pre-release" ]]; then
    # Add current timestamp for pre-release.
    # we can't use the git revision because not all python registries allow local version identifiers. 
    # Public version identifiers must conform to PEP 440 and only allow digits.
    TIMESTAMP=$(date +"%Y%m%d%H%M")
    VERSION="${BASE_VERSION}.dev.${TIMESTAMP}"
else
    VERSION="$BASE_VERSION"
fi

echo "Package name: $PACKAGE_NAME"
echo "Version: $VERSION"
echo "Release type: $RELEASE_TYPE"
echo

# Check if package already exists
if [[ $(curl -s -o /dev/null -w "%{http_code}" "$REGISTRY_CHECK_URL/$PACKAGE_NAME/$VERSION/json") == "200" ]]; then
    echo "⚠️ Package $PACKAGE_NAME version $VERSION already exists on PyPI  at $REGISTRY_CHECK_URL/$PACKAGE_NAME/$VERSION/json. Skipping publishing."
    exit 0
else
    echo "✅ Package $PACKAGE_NAME version $VERSION does not exist already on PyPI. Proceeding with publishing."
fi


# Assumes the connector uses Poetry for packaging and has a pyproject.toml
if [[ -f "pyproject.toml" ]]; then
    echo "Detected Poetry project"

    # runs automatically on script error or exit
    cleanup() {
        if [[ -f pyproject.toml.bak ]]; then
            mv pyproject.toml.bak pyproject.toml
            echo "Restored original pyproject.toml"
        fi
    }
    trap cleanup EXIT   

    # to support overriding the package name and the version when publishing to PyPI, the script modifies the pyproject.toml file 
    # we keep a backup at pyproject.toml.bak that is used to restore the initial state at the end
    # TODO: figure out if we can do this in a less hacky way and reevaluate whether to continue defining PyPI package information in metadata.yaml
    sed -i.bak -E \
        "s/^([[:space:]]*name[[:space:]]*=[[:space:]]*\").*(\".*)$/\\1${PACKAGE_NAME}\\2/;
        s/^([[:space:]]*version[[:space:]]*=[[:space:]]*\").*(\".*)$/\\1${VERSION}\\2/" \
        pyproject.toml

    echo "✅ Temporary override package name to '$PACKAGE_NAME' and version to '$VERSION' in pyproject.toml"

    # Configure Poetry for PyPI publishing
    poetry config repositories.mypypi "$REGISTRY_UPLOAD_URL"
    poetry config pypi-token.mypypi "$PYPI_TOKEN"

    # Default timeout is set to 15 seconds
    # We sometime face 443 HTTP read timeout responses from PyPi
    # Setting it to 60 seconds to avoid transient publish failures
    export POETRY_REQUESTS_TIMEOUT=60

    poetry publish --build --repository mypypi --no-interaction -vvv

else
    echo "⚠️ Error: No pyproject.toml, skipping publishing to PyPI" >&2
    exit 0
fi

echo "✅ Successfully published $PACKAGE_NAME ($VERSION) to PyPI ($REGISTRY_PACKAGE_URL/$PACKAGE_NAME/$VERSION)"