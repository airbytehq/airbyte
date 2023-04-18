FROM airbyte/source-zendesk-support:0.2.27

COPY --from=ghcr.io/estuary/airbyte-to-flow:dev /airbyte-to-flow ./
ENTRYPOINT ["/airbyte/integration_code/airbyte-to-flow", "--connector-entrypoint", "python /airbyte/integration_code/main.py"]

LABEL io.airbyte.version=v1
LABEL io.airbyte.name=airbyte/source-zendesk-support
LABEL FLOW_RUNTIME_PROTOCOL=capture
LABEL CONNECTOR_PROTOCOL=flow-capture
LABEL FLOW_RUNTIME_CODEC=json