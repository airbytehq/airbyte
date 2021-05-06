FROM python:3.7-slim

# We change to a directory unique to us
WORKDIR /airbyte/integration_code
# Install any needed python dependencies
RUN pip install pyarrow==4.0.0 requests snowflake-connector-python==2.4.3
# Copy source files
COPY source.py .
COPY spec.json .

# When this container is invoked, append the input argemnts to `python source.py`
ENTRYPOINT ["python", "/airbyte/integration_code/source.py"]

# Airbyte's build system uses these labels to know what to name and tag the docker images produced by this Dockerfile.
LABEL io.airbyte.name=airbyte/source-snowflake
LABEL io.airbyte.version=0.1.0

# docker build . -t airbyte/source-snowflake:dev
# docker run airbyte/source-snowflake:dev spec
# docker run -v $(pwd)/config.json:/data/config.json airbyte/source-snowflake:dev check --config /data/config.json

# docker run -v $(pwd)/config.json:/data/config.json airbyte/source-snowflake:dev discover --config /data/config.json
# docker run -v $(pwd)/config.json:/data/config.json -v $(pwd)/test_catalog.json:/data/test_catalog.json airbyte/source-snowflake:dev read --config /data/config.json --catalog /data/test_catalog.json