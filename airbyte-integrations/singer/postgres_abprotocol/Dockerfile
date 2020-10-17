FROM airbyte/integration-base-singer:dev

RUN apt-get update && apt-get install -y \
    jq libpq-dev gcc\
    && rm -rf /var/lib/apt/lists/*

ENV CODE_PATH="postgres_singer_source"
ENV AIRBYTE_IMPL_MODULE="postgres_singer_source"
ENV AIRBYTE_IMPL_PATH="PostgresSingerSource"

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/postgres-singer-source-abprotocol

WORKDIR /airbyte/integration_code

COPY $CODE_PATH ./$CODE_PATH
COPY setup.py ./
RUN pip install .

WORKDIR /airbyte
