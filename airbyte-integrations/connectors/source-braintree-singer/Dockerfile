FROM airbyte/integration-base-singer:0.1.1

RUN apt-get update && apt-get install -y bash jq && rm -rf /var/lib/apt/lists/*

ENV CODE_PATH="source_braintree_singer"
ENV AIRBYTE_IMPL_MODULE="source_braintree_singer"
ENV AIRBYTE_IMPL_PATH="SourceBraintreeSinger"
ENV AIRBYTE_ENTRYPOINT "/airbyte/base.sh"

LABEL io.airbyte.version=0.2.3
LABEL io.airbyte.name=airbyte/source-braintree-singer

WORKDIR /airbyte/integration_code
COPY $CODE_PATH ./$CODE_PATH
COPY setup.py ./
RUN pip install .

WORKDIR /airbyte

