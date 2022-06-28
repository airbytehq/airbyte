FROM python:3.9.11-alpine3.15 as base

# build and load all requirements
FROM base as builder
WORKDIR /airbyte/integration_code

# added second line to solve grpcio install problem (https://github.com/grpc/grpc/issues/24722)
# upgrade pip to the latest version
RUN apk --no-cache upgrade \
    && apk add --no-cache gcc g++ linux-headers \
    && pip install --upgrade pip \
    && apk --no-cache add tzdata build-base


COPY setup.py ./
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
RUN apk --no-cache add bash

# this is used by grpc
RUN apk --no-cache add libstdc++

# copy payload code only
COPY main.py ./
COPY destination_firestore ./destination_firestore

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.1.1
LABEL io.airbyte.name=airbyte/destination-firestore
