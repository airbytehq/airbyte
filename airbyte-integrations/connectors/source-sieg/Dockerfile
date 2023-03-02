FROM python:3.9-slim

# Bash is installed for more convenient debugging.
RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*

WORKDIR /airbyte/integration_code
COPY source_sieg ./source_sieg
COPY main.py ./
COPY setup.py ./
RUN pip install .
RUN pip install xmltodict
RUN pip install lxml

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.1.3
LABEL io.airbyte.name=airbyte/source-python-http-tutorial
