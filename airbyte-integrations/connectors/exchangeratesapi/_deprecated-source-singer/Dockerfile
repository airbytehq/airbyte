FROM python:3.7-alpine

WORKDIR /singer

ENV VIRTUAL_ENV=/singer/env
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apk add --no-cache jq bash

# Install dependencies:
COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
  pip install -r requirements.txt

COPY entrypoint.sh .
COPY ./src/test-integration/resources/spec.json .

ENTRYPOINT ["/singer/entrypoint.sh"]

LABEL io.airbyte.version=0.1.3
LABEL io.airbyte.name=airbyte/integration-singer-exchangeratesapi_io-source
