FROM python:3.9-slim

# Bash is installed for more convenient debugging.
RUN apt-get update && apt-get install -y bash automake build-essential git libtool libtool-bin autoconf && rm -rf /var/lib/apt/lists/*

WORKDIR /airbyte/integration_code
COPY ./airbyte-integrations/connectors/source-sendgrid/source_sendgrid ./source_sendgrid
RUN echo "$ls"

COPY ./airbyte-cdk/python ./cdk

COPY ./airbyte-integrations/connectors/source-sendgrid/main.py ./
COPY ./airbyte-integrations/connectors/source-sendgrid/setup.py ./

#COPY setup.py ./
RUN pip install -e ./cdk
RUN pip install .

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.2.7
LABEL io.airbyte.name=airbyte/source-sendgrid
