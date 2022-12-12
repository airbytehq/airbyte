FROM python:3.9-slim

# Bash is installed for more convenient debugging.
RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*

ENV CODE_PATH="source_exchange_rates"
ENV WORKDIR=/airbyte/integration_code

WORKDIR $WORKDIR
COPY $CODE_PATH ./$CODE_PATH
COPY setup.py ./
COPY main.py ./

RUN pip install .

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=1.2.7
LABEL io.airbyte.name=airbyte/source-exchange-rates
