FROM python:3.9-slim

# Bash is installed for more convenient debugging.
RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*

ENV CODE_PATH="source_slack"
ENV WORKDIR=/airbyte/integration_code

WORKDIR $WORKDIR

COPY setup.py ./
RUN pip install .

COPY $CODE_PATH ./$CODE_PATH
COPY main.py ./
COPY spec.patch.json ./
COPY oauth2.patch.json ./
COPY documentation_url.patch.json ./
COPY streams/* ./streams/

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
COPY --from=ghcr.io/estuary/airbyte-to-flow:dev /airbyte-to-flow ./
ENTRYPOINT ["/airbyte/integration_code/airbyte-to-flow", "--connector-entrypoint", "python /airbyte/integration_code/main.py"]

LABEL io.airbyte.version=v1
LABEL io.airbyte.name=airbyte/source-slack
LABEL FLOW_RUNTIME_PROTOCOL=capture
LABEL CONNECTOR_PROTOCOL=flow-capture
LABEL FLOW_RUNTIME_CODEC=json