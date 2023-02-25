FROM python:3.9.11-alpine3.15 as base

# alwyays update dependencies
RUN apk update && apk upgrade -a

# upgrade pip and install libs
RUN apk --no-cache upgrade \
    && pip install --upgrade pip \
    && apk --no-cache add tzdata build-base bash

# Install custom deps for this connector
RUN apk add libffi-dev musl-dev g++

# build and load all requirements
FROM base as builder
WORKDIR /airbyte/integration_code

COPY setup.py ./
# install necessary packages to a temporary folder
RUN pip install --prefix=/install .
# build a clean environment
FROM base
# RUN conda install -c conda-forge python-duckdb
WORKDIR /airbyte/integration_code

# copy all loaded and built libraries to a pure basic image
COPY --from=builder /install /usr/local
# add default timezone settings
COPY --from=builder /usr/share/zoneinfo/Etc/UTC /etc/localtime
RUN echo "Etc/UTC" > /etc/timezone

#adding duckdb manually (outside of setup.py - lots of errors)
RUN pip install duckdb

# copy payload code only
COPY main.py ./
COPY destination_duckdb ./destination_duckdb

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/destination-duckdb
