FROM python:3.9-slim

# We change to a directory unique to us
WORKDIR /airbyte/integration_code
# Install any needed Python dependencies
RUN pip install requests
# Copy source files
COPY source.py .
COPY spec.json .

# When this container is invoked, append the input argemnts to `python source.py`
ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/source.py"
ENTRYPOINT ["python", "/airbyte/integration_code/source.py"]

# Airbyte's build system uses these labels to know what to name and tag the docker images produced by this Dockerfile.
LABEL io.airbyte.name=airbyte/source-stock-ticker-api
LABEL io.airbyte.version=0.2.1
