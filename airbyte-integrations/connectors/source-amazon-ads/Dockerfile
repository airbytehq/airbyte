FROM airbyte/source-amazon-ads:1.0.3

COPY --from=ghcr.io/estuary/airbyte-to-flow:dev /airbyte-to-flow ./airbyte-to-flow
ENTRYPOINT ["/airbyte/integration_code/airbyte-to-flow", "--connector-entrypoint", "python /airbyte/integration_code/main.py"]

COPY *.patch.json ./

LABEL io.airbyte.version=v1
LABEL io.airbyte.name=airbyte/source-amazon-ads
LABEL FLOW_RUNTIME_PROTOCOL=capture
LABEL CONNECTOR_PROTOCOL=flow-capture
LABEL FLOW_RUNTIME_CODEC=json
