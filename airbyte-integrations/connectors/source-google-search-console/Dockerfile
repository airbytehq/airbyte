FROM python:3.7-slim

# Bash is installed for more convenient debugging.
RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*

WORKDIR /airbyte/integration_code
COPY source_google_search_console ./source_google_search_console
COPY main.py ./
COPY setup.py ./
RUN pip install .

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENV SENTRY_DSN "https://d4b03de0c4574c78999b8d58e55243dc@o1009025.ingest.sentry.io/6102835"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.1.11
LABEL io.airbyte.name=airbyte/source-google-search-console
