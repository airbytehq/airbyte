FROM airbyte/base-singer:dev

RUN apt-get update && apt-get install -y jq

COPY spec.json /airbyte/exchangeratesapi-files/spec.json

WORKDIR /airbyte/source_exchangeratesapi_singer

COPY source_exchangeratesapi_singer/__init__.py ./source_exchangeratesapi_singer/__init__.py
COPY source_exchangeratesapi_singer/source_exchangeratesapi_singer.py ./source_exchangeratesapi_singer/source_exchangeratesapi_singer.py

COPY setup.py .
RUN pip install .

WORKDIR /airbyte

ENV AIRBYTE_IMPL_MODULE="source_exchangeratesapi_singer"
ENV AIRBYTE_IMPL_PATH="SourceExchangeRatesApiSinger"

LABEL io.airbyte.version=0.1.2
