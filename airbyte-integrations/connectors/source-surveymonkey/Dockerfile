FROM airbyte/source-surveymonkey:0.1.16

COPY --from=ghcr.io/estuary/airbyte-to-flow:dev /airbyte-to-flow ./
ENTRYPOINT ["/airbyte/integration_code/airbyte-to-flow", "--connector-entrypoint", "python /airbyte/integration_code/main.py"]

COPY oauth2.patch.json ./
COPY spec.patch.json ./
COPY spec.map.json ./
COPY streams/* ./streams/
COPY documentation_url.patch.json ./

LABEL io.airbyte.version=v1
LABEL io.airbyte.name=airbyte/source-surveymonkey
LABEL FLOW_RUNTIME_PROTOCOL=capture
LABEL CONNECTOR_PROTOCOL=flow-capture
LABEL FLOW_RUNTIME_CODEC=json
