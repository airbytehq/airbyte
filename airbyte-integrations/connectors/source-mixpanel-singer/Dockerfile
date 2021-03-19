FROM airbyte/integration-base-singer:0.1.0

# Bash is installed for more convenient debugging.
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update \
    && apt-get install -y bash \
    && apt-get install -y gcc \
    && rm -rf /var/lib/apt/lists/*

ENV CODE_PATH="source_mixpanel_singer"
ENV AIRBYTE_IMPL_MODULE="source_mixpanel_singer"
ENV AIRBYTE_IMPL_PATH="SourceMixpanelSinger"

WORKDIR /airbyte/integration_code
COPY $CODE_PATH ./$CODE_PATH
COPY setup.py ./

RUN pip install .

LABEL io.airbyte.version=0.2.0
LABEL io.airbyte.name=airbyte/source-mixpanel-singer
