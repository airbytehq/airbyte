FROM airbyte/base-singer:dev

RUN apt-get update && apt-get install -y jq curl bash

COPY spec.json /airbyte/stripe-files/spec.json

WORKDIR /airbyte/source_stripe_singer

COPY source_stripe_singer/*.py ./source_stripe_singer/

COPY setup.py .
RUN pip install .

WORKDIR /airbyte

ENV AIRBYTE_IMPL_MODULE="source_stripe_singer"
ENV AIRBYTE_IMPL_PATH="SourceStripeSinger"

LABEL io.airbyte.version=0.1.3

