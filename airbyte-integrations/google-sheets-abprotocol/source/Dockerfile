FROM airbyte/integration-base-python:dev

RUN apt-get update && apt-get install -y jq curl bash

WORKDIR /airbyte/google_sheets_source


COPY ./google_sheets_source google_sheets_source
COPY ./spec.json .
COPY setup.py .
RUN pip install .

ENV AIRBYTE_IMPL_MODULE="google_sheets_source"
ENV AIRBYTE_IMPL_PATH="GoogleSheetsSource"

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/google-sheets-source-abprotocol
