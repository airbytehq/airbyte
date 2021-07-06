FROM airbyte/integration-base-singer:0.1.1

RUN apt-get update && apt-get install -y \
    jq gcc \
    && rm -rf /var/lib/apt/lists/*

ENV CODE_PATH="source_googleanalytics_singer"
ENV AIRBYTE_IMPL_MODULE="source_googleanalytics_singer"
ENV AIRBYTE_IMPL_PATH="GoogleAnalyticsSingerSource"
ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/source.py"

LABEL io.airbyte.version=0.2.6
LABEL io.airbyte.name=airbyte/source-googleanalytics-singer

WORKDIR /airbyte/integration_code
COPY $CODE_PATH ./$CODE_PATH
COPY setup.py ./
RUN pip install .

WORKDIR /airbyte
