FROM airbyte/integration-base-python:0.1.0

RUN apt-get update && apt-get install -y jq curl bash && rm -rf /var/lib/apt/lists/*

ENV CODE_PATH="source_http_request"
ENV AIRBYTE_IMPL_MODULE="source_http_request"
ENV AIRBYTE_IMPL_PATH="SourceHttpRequest"

WORKDIR /airbyte/integration_code
COPY $CODE_PATH ./$CODE_PATH
COPY setup.py ./
RUN pip install .

LABEL io.airbyte.version=0.2.1
LABEL io.airbyte.name=airbyte/source-http-request
