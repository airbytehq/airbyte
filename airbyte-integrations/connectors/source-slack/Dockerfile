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

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.1.17
LABEL io.airbyte.name=airbyte/source-slack
