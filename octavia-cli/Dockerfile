FROM python:3.9.11-alpine3.15 as base

# alwyays update dependencies
RUN apk update && apk upgrade -a

RUN apt-get upgrade \
    && pip install --upgrade pip

WORKDIR /home/octavia-cli
COPY . ./

RUN pip install --no-cache-dir .

RUN useradd --create-home --shell /bin/bash octavia-cli
USER octavia-cli

WORKDIR /home/octavia-project
ENTRYPOINT ["octavia"]

LABEL io.airbyte.version=0.41.0
LABEL io.airbyte.name=airbyte/octavia-cli
