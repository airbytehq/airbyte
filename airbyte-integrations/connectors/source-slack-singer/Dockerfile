FROM airbyte/integration-base-singer:dev

RUN apt-get update && apt-get install -y bash gcc && rm -rf /var/lib/apt/lists/*

ENV CODE_PATH="source_slack_singer"
ENV AIRBYTE_IMPL_MODULE="source_slack_singer"
ENV AIRBYTE_IMPL_PATH="SourceSlackSinger"

LABEL io.airbyte.version=0.1.4
LABEL io.airbyte.name=airbyte/source-slack-singer

WORKDIR /airbyte/integration_code
COPY $CODE_PATH ./$CODE_PATH
COPY setup.py ./
RUN pip install ".[main]"

WORKDIR /airbyte

