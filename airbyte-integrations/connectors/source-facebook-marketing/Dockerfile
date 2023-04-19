ARG AIRBYTE_TO_FLOW_TAG="dev"
FROM ghcr.io/estuary/airbyte-to-flow:$AIRBYTE_TO_FLOW_TAG as airbyte-to-flow

FROM airbyte/source-facebook-marketing:0.3.3

COPY --from=airbyte-to-flow /airbyte-to-flow ./
ENTRYPOINT ["/airbyte/integration_code/airbyte-to-flow", "--connector-entrypoint", "python /airbyte/integration_code/main.py"]

COPY spec.patch.json ./
COPY spec.map.json ./
COPY documentation_url.patch.json ./
COPY oauth2.patch.json ./
COPY streams/* ./streams/

LABEL io.airbyte.version=v4
LABEL io.airbyte.name=airbyte/source-facebook-marketing
LABEL FLOW_RUNTIME_PROTOCOL=capture
LABEL CONNECTOR_PROTOCOL=flow-capture
LABEL FLOW_RUNTIME_CODEC=json
