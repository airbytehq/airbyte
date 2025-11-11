FROM airbyte/python-connector-base:1.0.0

WORKDIR /airbyte/integration_code

# Copy source code
COPY source_airmeet ./source_airmeet
COPY main.py ./
COPY setup.py ./
COPY requirements.txt ./

# Install the connector
RUN pip install --no-cache-dir -e .

# Set the entrypoint
ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

# Metadata
LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/source-airmeet