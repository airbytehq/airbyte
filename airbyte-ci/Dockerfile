FROM python:3.10

RUN apt-get update && apt-get install git

COPY . /airbyte-ci
RUN pip install /airbyte-ci/connectors/pipelines
RUN mkdir /airbyte

WORKDIR /airbyte
