FROM airbyte/airbyte-cdk-connectors

# Bash is installed for more convenient debugging.
RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*

WORKDIR /airbyte/integration_code

COPY setup.py ./

ARG USE_LOCAL_CDK
RUN USE_LOCAL_CDK=$USE_LOCAL_CDK LOCAL_CDK_DIR=$LOCAL_CDK_DIR pip install .

COPY source_greenhouse ./source_greenhouse
COPY main.py ./

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.3.0
LABEL io.airbyte.name=airbyte/source-greenhouse
