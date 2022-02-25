FROM python:3.8.12-slim as base

RUN apt-get upgrade \
    && pip install --upgrade pip

WORKDIR /home/octavia-cli
COPY . ./

RUN pip install -e .\[dev\]

RUN useradd --create-home --shell /bin/bash octavia-cli
USER octavia-cli

RUN mkdir -p /tmp/octavia-config
WORKDIR /tmp/octavia-config

ENTRYPOINT ["octavia"]

LABEL io.airbyte.version=dev
LABEL io.airbyte.name=airbyte/octavia-cli
