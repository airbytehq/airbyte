ARG AIRBYTE_TO_FLOW_TAG="dev"
FROM ghcr.io/estuary/airbyte-to-flow:$AIRBYTE_TO_FLOW_TAG as airbyte-to-flow

FROM airbyte/source-google-analytics-v4:0.1.34

COPY --from=airbyte-to-flow /airbyte-to-flow ./
ENTRYPOINT ["/airbyte/integration_code/airbyte-to-flow", "--connector-entrypoint", "python /airbyte/integration_code/main.py"]

COPY documentation_url.patch.json ./
COPY spec.patch.json ./
COPY oauth2.patch.json ./
COPY streams/* ./streams/

LABEL io.airbyte.version=v2
LABEL io.airbyte.name=airbyte/source-google-analytics-v4
LABEL FLOW_RUNTIME_PROTOCOL=capture
LABEL CONNECTOR_PROTOCOL=flow-capture
LABEL FLOW_RUNTIME_CODEC=json