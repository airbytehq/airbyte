FROM airbyte/source-exchange-rates:1.2.8

COPY --from=ghcr.io/estuary/airbyte-to-flow:dev /airbyte-to-flow ./airbyte-to-flow
ENTRYPOINT ["/airbyte/integration_code/airbyte-to-flow", "--connector-entrypoint", "python /airbyte/integration_code/main.py"]

COPY spec.patch.json ./
COPY documentation_url.patch.json ./

LABEL io.airbyte.version=v2
LABEL io.airbyte.name=airbyte/source-exchange-rates
LABEL FLOW_RUNTIME_PROTOCOL=capture
LABEL CONNECTOR_PROTOCOL=flow-capture
LABEL FLOW_RUNTIME_CODEC=json
