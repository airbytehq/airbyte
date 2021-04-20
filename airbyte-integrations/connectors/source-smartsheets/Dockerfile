FROM airbyte/integration-base-python:0.1.1

# Bash is installed for more convenient debugging.
RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*

ENV CODE_PATH="source_smartsheets"
ENV AIRBYTE_IMPL_MODULE="source_smartsheets"
ENV AIRBYTE_IMPL_PATH="SourceSmartsheets"

WORKDIR /airbyte/integration_code
COPY $CODE_PATH ./$CODE_PATH
COPY setup.py ./
RUN pip install .

LABEL io.airbyte.version=0.1.1
LABEL io.airbyte.name=airbyte/source-smartsheets
