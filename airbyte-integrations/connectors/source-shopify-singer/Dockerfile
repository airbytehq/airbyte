FROM airbyte/integration-base-singer:0.1.0

# Bash is installed for more convenient debugging.
RUN apt-get update && apt-get install -y bash gcc && rm -rf /var/lib/apt/lists/*

ENV CODE_PATH="source_shopify_singer"
ENV AIRBYTE_IMPL_MODULE="source_shopify_singer"
ENV AIRBYTE_IMPL_PATH="SourceShopifySinger"

WORKDIR /airbyte/integration_code
COPY $CODE_PATH ./$CODE_PATH
COPY setup.py ./
RUN pip install https://github.com/airbytehq/tap-shopify/tarball/master
RUN pip install .

LABEL io.airbyte.version=0.2.0
LABEL io.airbyte.name=airbyte/source-shopify-singer
