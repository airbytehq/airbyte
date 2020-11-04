FROM airbyte/integration-base-singer:dev

RUN apt-get update && apt-get install -y \
    jq gcc \
    && rm -rf /var/lib/apt/lists/*

ENV CODE_PATH="source_googleanalytics_singer"
ENV AIRBYTE_IMPL_MODULE="source_googleanalytics_singer"
ENV AIRBYTE_IMPL_PATH="GoogleAnalyticsSingerSource"

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/source-googleanalytics-singer

WORKDIR /airbyte/integration_code
COPY $CODE_PATH ./$CODE_PATH
COPY setup.py ./
RUN pip install ".[main]"

WORKDIR /airbyte
