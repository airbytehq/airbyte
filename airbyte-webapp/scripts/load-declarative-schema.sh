set -e
mkdir -p build

if [ -z "$CDK_VERSION" ]
then
    version="0.25.0"
fi


if [ -z "$CDK_MANIFEST_PATH" ]
then
    echo "Downloading CDK manifest $version from pypi"
    curl -L https://pypi.python.org/packages/source/a/airbyte-cdk/airbyte-cdk-${version}.tar.gz | tar -xzO airbyte-cdk-${version}/airbyte_cdk/sources/declarative/declarative_component_schema.yaml > build/declarative_component_schema.yaml
else
    echo "Copying local CDK manifest version from $CDK_MANIFEST_PATH"
    cp ${CDK_MANIFEST_PATH} build/declarative_component_schema.yaml
fi