FROM airbyte/integration-base-singer:dev

# GCC is needed by the ciso8601, a dependency of tap-facebook.
# See https://github.com/closeio/ciso8601/issues/98 for more information.
RUN apt-get update && apt-get install -y gcc bash && rm -rf /var/lib/apt/lists/*

ENV CODE_PATH="source_facebook_marketing_api_singer"
ENV AIRBYTE_IMPL_MODULE="source_facebook_marketing_api_singer"
ENV AIRBYTE_IMPL_PATH="SourceFacebookMarketingApiSinger"

WORKDIR /airbyte/integration_code
COPY $CODE_PATH ./$CODE_PATH
COPY setup.py ./
RUN pip install .

LABEL io.airbyte.version=0.1.4
LABEL io.airbyte.name=airbyte/source-facebook-marketing-api-singer
