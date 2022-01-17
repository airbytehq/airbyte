FROM airbyte/integration-base-singer:0.1.1

# Bash is installed for more convenient debugging.
RUN apt-get update \
    && apt-get install -y git \
    && apt-get install -y bash \
    && apt-get install -y gcc \
    && rm -rf /var/lib/apt/lists/*

ENV CODE_PATH="source_googleanalytics_singer"
ENV AIRBYTE_IMPL_MODULE="source_googleanalytics_singer"
ENV AIRBYTE_IMPL_PATH="GoogleAnalyticsSingerSource"
ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"

WORKDIR /airbyte/integration_code
COPY $CODE_PATH ./$CODE_PATH
COPY main.py ./
COPY setup.py ./
RUN pip install .

ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]
LABEL io.airbyte.version=0.2.17
LABEL io.airbyte.name=blotout/source-googleanalytics-singer
