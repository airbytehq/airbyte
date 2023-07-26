FROM python:3.9.17-alpine3.18

# Bash is installed for more convenient debugging.
RUN apk update && apk upgrade && apk add bash
RUN apk add make automake gcc g++ subversion python3-dev

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"

WORKDIR /airbyte/integration_code
COPY source_salesforce ./source_salesforce
COPY setup.py ./
COPY main.py ./
RUN pip install .

ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=2.1.2
LABEL io.airbyte.name=airbyte/source-salesforce
