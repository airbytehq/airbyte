FROM nickgryg/alpine-pandas:3.9.12 as base

# build and load all requirements
FROM base as builder
WORKDIR /airbyte/integration_code

# upgrade pip to the latest version
RUN apk --no-cache upgrade \
    && pip install --upgrade pip \
    && apk --no-cache add tzdata build-base swig libffi-dev libstdc++

COPY setup.py ./

RUN pip install --upgrade pip

## Workaround for https://github.com/yaml/pyyaml/issues/601
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
RUN apk --no-cache add bash

# copy payload code only
COPY main.py ./
COPY destination_langchain ./destination_langchain

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.0.2
LABEL io.airbyte.name=airbyte/destination-langchain
