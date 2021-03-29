FROM airbyte/integration-base-singer:0.1.0

RUN apt-get update && apt-get install -y \
    jq \
    curl \
    bash \
    && rm -rf /var/lib/apt/lists/*

ENV CODE_PATH="source_stripe_singer"
ENV AIRBYTE_IMPL_MODULE="source_stripe_singer"
ENV AIRBYTE_IMPL_PATH="SourceStripeSinger"

LABEL io.airbyte.version=0.2.0
LABEL io.airbyte.name=airbyte/source-stripe-singer

WORKDIR /airbyte/integration_code
COPY $CODE_PATH ./$CODE_PATH
COPY setup.py ./
RUN pip install .

WORKDIR /airbyte

