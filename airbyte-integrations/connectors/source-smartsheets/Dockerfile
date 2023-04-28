FROM python:3.9-slim

# Bash is installed for more convenient debugging.
RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*

ENV CODE_PATH="source_smartsheets"

WORKDIR /airbyte/integration_code
COPY setup.py ./
RUN pip install .
COPY main.py ./
COPY $CODE_PATH ./$CODE_PATH

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=1.0.1
LABEL io.airbyte.name=airbyte/source-smartsheets
