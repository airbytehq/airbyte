FROM python:3.7-slim

WORKDIR /airbyte/integration_code
RUN pip install requests
COPY source.py .
COPY spec.json .

ENTRYPOINT ["python", "/airbyte/integration_code/source.py"]

# Airbyte's build system uses these labels to know what to name and tag the docker images produced by this Dockerfile.
LABEL io.airbyte.name=airbyte/source-stock-ticker-api
LABEL io.airbyte.version=0.2.0
