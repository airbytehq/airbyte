FROM airbyte/integration-base-singer:dev

RUN apt-get update && apt-get install -y bash gcc && rm -rf /var/lib/apt/lists/*

ENV CODE_PATH="source_twilio_singer"
ENV AIRBYTE_IMPL_MODULE="source_twilio_singer"
ENV AIRBYTE_IMPL_PATH="SourceTwilioSinger"

LABEL io.airbyte.version=0.2.0
LABEL io.airbyte.name=airbyte/source-twilio-singer

WORKDIR /airbyte/integration_code
COPY $CODE_PATH ./$CODE_PATH
COPY setup.py ./
RUN pip install ".[main]"

WORKDIR /airbyte

