FROM python:3.10.0-slim as base

RUN apt-get upgrade \
    && pip install --upgrade pip

WORKDIR /home/octavia-cli
COPY . ./

RUN pip install --no-cache-dir .

RUN useradd --create-home --shell /bin/bash octavia-cli
USER octavia-cli

ENTRYPOINT ["octavia"]

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/octavia-cli
