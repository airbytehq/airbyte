FROM airbyte/source-mailchimp:0.3.5

COPY --from=ghcr.io/estuary/airbyte-to-flow:dev /airbyte-to-flow ./
ENTRYPOINT ["/airbyte/integration_code/airbyte-to-flow", "--connector-entrypoint", "python /airbyte/integration_code/main.py"]

COPY documentation_url.patch.json ./
COPY spec.patch.json ./
COPY oauth2.patch.json ./
COPY streams/* ./streams/

LABEL io.airbyte.version=v2
LABEL io.airbyte.name=airbyte/source-mailchimp
LABEL FLOW_RUNTIME_PROTOCOL=capture
LABEL CONNECTOR_PROTOCOL=flow-capture
LABEL FLOW_RUNTIME_CODEC=json