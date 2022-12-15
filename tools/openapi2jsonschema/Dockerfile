FROM python:3.9-slim

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

RUN pip install git+https://github.com/airbytehq/openapi2jsonschema.git@v0.1

RUN mkdir -p /schemas

WORKDIR /schemas

ENTRYPOINT ["/usr/local/bin/openapi2jsonschema"]
