FROM airbyte/source-linkedin-ads:0.1.15

COPY --from=ghcr.io/estuary/airbyte-to-flow:dev /airbyte-to-flow ./
ENTRYPOINT ["/airbyte/integration_code/airbyte-to-flow", "--connector-entrypoint", "python /airbyte/integration_code/main.py"]

COPY documentation_url.patch.json ./
COPY spec.patch.json ./
COPY oauth2.patch.json ./

LABEL io.airbyte.version=v2
LABEL io.airbyte.name=airbyte/source-linkedin-ads
LABEL FLOW_RUNTIME_PROTOCOL=capture
LABEL CONNECTOR_PROTOCOL=flow-capture
LABEL FLOW_RUNTIME_CODEC=json