FROM airbyte/integration-base-singer:0.1.1

# Bash is installed for more convenient debugging.
RUN apt-get update && apt-get install -y bash -y gcc && rm -rf /var/lib/apt/lists/*

ENV CODE_PATH="source_google_search_console_singer"
ENV AIRBYTE_IMPL_MODULE="source_google_search_console_singer"
ENV AIRBYTE_IMPL_PATH="SourceGoogleSearchConsoleSinger"
ENV AIRBYTE_ENTRYPOINT "/airbyte/base.sh"

WORKDIR /airbyte/integration_code
COPY $CODE_PATH ./$CODE_PATH
COPY setup.py ./
RUN pip install .

LABEL io.airbyte.version=0.1.3
LABEL io.airbyte.name=airbyte/source-google-search-console-singer
