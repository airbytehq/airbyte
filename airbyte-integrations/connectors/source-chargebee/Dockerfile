FROM python:3.9.11-alpine3.15 as base

# alwyays update dependencies
RUN apk update && apk upgrade -a

# upgrade pip and install libs
RUN apk --no-cache upgrade \
    && pip install --upgrade pip \
    && apk --no-cache add tzdata build-base bash

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"

WORKDIR /airbyte/integration_code
COPY source_chargebee ./source_chargebee
COPY main.py ./
COPY setup.py ./
RUN pip install .

ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.2.1
LABEL io.airbyte.name=airbyte/source-chargebee
