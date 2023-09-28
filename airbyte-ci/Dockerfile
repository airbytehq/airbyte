FROM python:3.10

RUN apt-get update && apt-get install git docker.io -y
RUN docker --version && git --version

COPY . /airbyte-ci
RUN pip install /airbyte-ci/connectors/pipelines
RUN airbyte-ci --version

RUN mkdir /airbyte

WORKDIR /airbyte
ENTRYPOINT [ "airbyte-ci" ]
CMD [ "--help" ]
