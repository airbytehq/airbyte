ARG AIRBYTE_TO_FLOW_TAG="dev"
FROM ghcr.io/estuary/airbyte-to-flow:$AIRBYTE_TO_FLOW_TAG as airbyte-to-flow

FROM airbyte/source-redshift:0.3.16

COPY --from=airbyte-to-flow /airbyte-to-flow ./
ENTRYPOINT ["/airbyte/airbyte-to-flow", "--connector-entrypoint", "/airbyte/base.sh"]

COPY *.json ./
COPY streams/* ./streams/

LABEL io.airbyte.version=v1
LABEL io.airbyte.name=airbyte/source-redshift
LABEL FLOW_RUNTIME_PROTOCOL=capture
LABEL CONNECTOR_PROTOCOL=flow-capture
LABEL FLOW_RUNTIME_CODEC=json
