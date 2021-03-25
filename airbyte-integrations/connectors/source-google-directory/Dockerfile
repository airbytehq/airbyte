FROM airbyte/integration-base-python:0.1.0

# Bash is installed for more convenient debugging.
RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*

ENV CODE_PATH="source_google_directory"
ENV AIRBYTE_IMPL_MODULE="source_google_directory"
ENV AIRBYTE_IMPL_PATH="SourceGoogleDirectory"

WORKDIR /airbyte/integration_code
COPY $CODE_PATH ./$CODE_PATH
COPY setup.py ./
RUN pip install ".[main]"

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/source-google-directory
