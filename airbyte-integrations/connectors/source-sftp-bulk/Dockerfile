FROM python:3.9-slim
# FROM python:3.9.11-alpine3.15

# Bash is installed for more convenient debugging.
# RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*

WORKDIR /airbyte/integration_code
COPY source_sftp_bulk ./source_sftp_bulk
COPY main.py ./
COPY setup.py ./
RUN pip install .

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/source-sftp-bulk
