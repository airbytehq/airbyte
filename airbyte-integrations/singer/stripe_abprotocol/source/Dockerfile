FROM airbyte/integration-base-singer:dev

RUN apt-get update && apt-get install -y \
    jq \
    curl \
    bash \
    && rm -rf /var/lib/apt/lists/*

ENV CODE_PATH="source_stripe_singer"
ENV AIRBYTE_IMPL_MODULE="source_stripe_singer"
ENV AIRBYTE_IMPL_PATH="SourceStripeSinger"

LABEL io.airbyte.version=0.1.3
LABEL io.airbyte.name=airbyte/source-stripe-abprotocol-singer

WORKDIR /airbyte/integration_code
COPY $CODE_PATH ./$CODE_PATH
COPY setup.py ./
RUN pip install .

WORKDIR /airbyte

