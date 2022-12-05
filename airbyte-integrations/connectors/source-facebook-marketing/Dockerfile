FROM python:3.9-slim

# Bash is installed for more convenient debugging.
RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*

WORKDIR /airbyte/integration_code
COPY source_facebook_marketing ./source_facebook_marketing
COPY main.py ./
COPY setup.py ./
RUN pip install .
COPY spec.patch.json ./
COPY spec.map.json ./
COPY documentation_url.patch.json ./
COPY oauth2.patch.json ./
COPY streams/* ./

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
COPY --from=ghcr.io/estuary/airbyte-to-flow:dev /airbyte-to-flow ./
ENTRYPOINT ["/airbyte/integration_code/airbyte-to-flow", "--connector-entrypoint", "python /airbyte/integration_code/main.py"]


LABEL io.airbyte.version=v3
LABEL io.airbyte.name=airbyte/source-facebook-marketing
LABEL FLOW_RUNTIME_PROTOCOL=capture
LABEL CONNECTOR_PROTOCOL=flow-capture
