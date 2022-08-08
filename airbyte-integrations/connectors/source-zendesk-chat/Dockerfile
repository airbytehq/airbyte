FROM python:3.9-slim

# Bash is installed for more convenient debugging.
RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*

ENV CODE_PATH="source_zendesk_chat"
ENV AIRBYTE_IMPL_MODULE="source_zendesk_chat"
ENV AIRBYTE_IMPL_PATH="SourceZendeskChat"
ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main_dev.py"

WORKDIR /airbyte/integration_code
COPY $CODE_PATH ./$CODE_PATH
COPY main_dev.py ./
COPY setup.py ./
RUN pip install .

ENTRYPOINT ["python", "/airbyte/integration_code/main_dev.py"]

LABEL io.airbyte.version=0.1.8
LABEL io.airbyte.name=airbyte/source-zendesk-chat
