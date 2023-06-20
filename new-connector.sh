export NAME=$1
export VERSION=$2

connectors="airbyte-integrations/connectors"

cp -R $connectors/source-template $connectors/source-$NAME
export DOCUMENTATION_URL="https://go.estuary.dev/source-$NAME"
export AIRBYTE_TO_FLOW_TAG='$AIRBYTE_TO_FLOW_TAG'
cat $connectors/source-template/Dockerfile | envsubst > $connectors/source-$NAME/Dockerfile
cat $connectors/source-template/documentation_url.patch.json | envsubst > $connectors/source-$NAME/documentation_url.patch.json