FROM airbyte/integration-base-singer:dev

RUN apt-get update && apt-get install -y jq gcc curl bash && rm -rf /var/lib/apt/lists/*

ENV CODE_PATH="source_facebook_marketing_api_singer"
ENV AIRBYTE_IMPL_MODULE="source_facebook_marketing_api_singer"
ENV AIRBYTE_IMPL_PATH="SourceFacebookMarketingApiSinger"

WORKDIR /airbyte/integration_code
COPY $CODE_PATH ./$CODE_PATH
COPY setup.py ./
RUN pip install --upgrade pip setuptools wheel && \
    pip install ".[main]"

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/source-facebook-marketing-api-singer
