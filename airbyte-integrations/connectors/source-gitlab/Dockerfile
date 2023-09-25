FROM python:3.9-slim

# Bash is installed for more convenient debugging.
RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"

WORKDIR /airbyte/integration_code
COPY setup.py ./
RUN pip install .
COPY source_gitlab ./source_gitlab
COPY main.py ./

ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=1.6.0
LABEL io.airbyte.name=airbyte/source-gitlab
