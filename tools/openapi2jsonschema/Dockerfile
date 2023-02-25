FROM python:3.9.11-alpine3.15 as base

# alwyays update dependencies
RUN apk update && apk upgrade -a

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

RUN pip install git+https://github.com/airbytehq/openapi2jsonschema.git@v0.1

RUN mkdir -p /schemas

WORKDIR /schemas

ENTRYPOINT ["/usr/local/bin/openapi2jsonschema"]
