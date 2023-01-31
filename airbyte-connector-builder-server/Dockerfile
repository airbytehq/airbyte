FROM python:3.9-slim as base

RUN apt-get upgrade \
    && pip install --upgrade pip

WORKDIR /home/connector-builder-server
COPY . ./

RUN pip install --no-cache-dir .

ENTRYPOINT ["uvicorn", "connector_builder.entrypoint:app", "--host", "0.0.0.0", "--port", "80"]

LABEL io.airbyte.version=0.40.32
LABEL io.airbyte.name=airbyte/connector-builder-server
