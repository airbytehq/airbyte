FROM airbyte/integration-base-python:0.1.1

# Bash is installed for more convenient debugging.
RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*

ENV CODE_PATH="source_freshdesk"
ENV AIRBYTE_IMPL_MODULE="source_freshdesk"
ENV AIRBYTE_IMPL_PATH="SourceFreshdesk"

WORKDIR /airbyte/integration_code
COPY $CODE_PATH ./$CODE_PATH
COPY setup.py ./
RUN pip install .

ENV AIRBYTE_ENTRYPOINT "/airbyte/base.sh"

LABEL io.airbyte.version=0.2.6
LABEL io.airbyte.name=airbyte/source-freshdesk
