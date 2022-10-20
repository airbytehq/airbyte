FROM python:3.9-slim as base

RUN apt-get upgrade \
    && pip install --upgrade pip

WORKDIR /home/connector-builder
COPY . ./

RUN pip install --no-cache-dir .

RUN useradd --create-home --shell /bin/bash connector-builder
USER connector-builder

WORKDIR /home/connector-builder

LABEL io.airbyte.version=0.40.15
LABEL io.airbyte.name=airbyte/connector-builder

CMD ["uvicorn", "connector_builder.entrypoint:app", "--host", "0.0.0.0", "--port", "80"]
