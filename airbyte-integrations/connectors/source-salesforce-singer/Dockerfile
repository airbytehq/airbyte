FROM airbyte/integration-base-singer:0.1.2

RUN apt-get update \
    && apt-get install -y bash \
    && apt-get install -y gcc \
    && rm -rf /var/lib/apt/lists/*

ENV CODE_PATH="source_salesforce_singer"
ENV AIRBYTE_IMPL_MODULE="source_salesforce_singer"
ENV AIRBYTE_IMPL_PATH="SourceSalesforceSinger"
ENV AIRBYTE_ENTRYPOINT "/airbyte/base.sh"

LABEL io.airbyte.version=0.2.5
LABEL io.airbyte.name=airbyte/source-salesforce-singer

WORKDIR /airbyte/integration_code
COPY $CODE_PATH ./$CODE_PATH
COPY setup.py ./
RUN pip install .

WORKDIR /airbyte

