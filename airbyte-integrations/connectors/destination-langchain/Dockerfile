FROM python:3.10-slim as base

# build and load all requirements
FROM base as builder
WORKDIR /airbyte/integration_code

# upgrade pip to the latest version

RUN apt-get update \
    && pip install --upgrade pip \
    && apt-get install -y build-essential cmake g++ libffi-dev libstdc++6

COPY setup.py ./

RUN pip install --upgrade pip

# This is required because the current connector dependency is not compatible with the CDK version
# An older CDK version will be used, which depends on pyYAML 5.4, for which we need to pin Cython to <3.0
# As of today the CDK version that satisfies the main dependency requirements, is 0.1.80 ...
RUN pip install --prefix=/install "Cython<3.0" "pyyaml~=5.4" --no-build-isolation

# install necessary packages to a temporary folder
RUN pip install --prefix=/install .

# build a clean environment
FROM base
WORKDIR /airbyte/integration_code

# copy all loaded and built libraries to a pure basic image
COPY --from=builder /install /usr/local
# add default timezone settings
COPY --from=builder /usr/share/zoneinfo/Etc/UTC /etc/localtime
RUN echo "Etc/UTC" > /etc/timezone

# bash is installed for more convenient debugging.
RUN apt-get install bash

# copy payload code only
COPY main.py ./
COPY destination_langchain ./destination_langchain

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.1.2
LABEL io.airbyte.name=airbyte/destination-langchain
