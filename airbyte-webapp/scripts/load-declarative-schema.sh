# This script makes sure the json schema for the low code connector manifest is provided for orval to build the Typescript types
# used by the connector builder UI. It either downloads a released version from PyPI or copies it over from a specified file path.

set -e
mkdir -p build

DEFAULT_CDK_VERSION=`cat ../airbyte-connector-builder-server/CDK_VERSION`

if [ -z "$CDK_VERSION" ]
then
    CDK_VERSION=$DEFAULT_CDK_VERSION
fi


if [ -z "$CDK_MANIFEST_PATH" ]
then
    TARGET_FILE="build/declarative_component_schema-${CDK_VERSION}.yaml"
    if [ ! -f "$TARGET_FILE" ]; then
        echo "Downloading CDK manifest schema $CDK_VERSION from pypi"
        curl -L https://pypi.python.org/packages/source/a/airbyte-cdk/airbyte-cdk-${CDK_VERSION}.tar.gz | tar -xzO airbyte-cdk-${CDK_VERSION}/airbyte_cdk/sources/declarative/declarative_component_schema.yaml > ${TARGET_FILE}
    else
        echo "Found cached CDK manifest schema $CDK_VERSION"
    fi
    cp ${TARGET_FILE} build/declarative_component_schema.yaml
else
    echo "Copying local CDK manifest version from $CDK_MANIFEST_PATH"
    cp ${CDK_MANIFEST_PATH} build/declarative_component_schema.yaml
fi