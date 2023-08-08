FROM python:3.10-slim

# Bash is installed for more convenient debugging.
# RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*

WORKDIR /airbyte/integration_code
COPY main.py ./
COPY setup.py ./
RUN pip install .

COPY destination_aws_datalake ./destination_aws_datalake

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.1.4
LABEL io.airbyte.name=airbyte/destination-aws-datalake
