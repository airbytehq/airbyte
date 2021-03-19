FROM airbyte/integration-base-singer:0.1.0

# Bash is installed for more convenient debugging.
# GCC is needed for CISO8601, a dependency of tap-marketo.
# See https://github.com/closeio/ciso8601/issues/98 for more information.
RUN apt-get update && apt-get install -y bash gcc && rm -rf /var/lib/apt/lists/*

ENV CODE_PATH="source_marketo_singer"
ENV AIRBYTE_IMPL_MODULE="source_marketo_singer"
ENV AIRBYTE_IMPL_PATH="SourceMarketoSinger"

WORKDIR /airbyte/integration_code
COPY $CODE_PATH ./$CODE_PATH
COPY setup.py ./
RUN pip install .

LABEL io.airbyte.version=0.2.0
LABEL io.airbyte.name=airbyte/source-marketo-singer
