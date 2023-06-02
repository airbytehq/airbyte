FROM python:3.9-slim as base

RUN apt-get upgrade \
    && pip install --upgrade pip

WORKDIR /home/octavia-cli
COPY . ./

RUN pip install --no-cache-dir .

RUN useradd --create-home --shell /bin/bash octavia-cli
USER octavia-cli

WORKDIR /home/octavia-project
ENTRYPOINT ["octavia"]

LABEL io.airbyte.version=0.44.9
LABEL io.airbyte.name=airbyte/octavia-cli
