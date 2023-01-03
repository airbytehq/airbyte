FROM python:3.9-slim as base

# build and load all requirements
FROM base as builder
WORKDIR /airbyte/integration_code

COPY setup.py ./
# install necessary packages to a temporary folder
RUN pip3 install --prefix=/install --no-cache-dir .

# build a clean environment
FROM base
WORKDIR /airbyte/integration_code

# copy all loaded and built libraries to a pure basic image
COPY --from=builder /install /usr/local
# add default timezone settings
COPY --from=builder /usr/share/zoneinfo/Etc/UTC /etc/localtime
RUN echo "Etc/UTC" > /etc/timezone

# copy payload code only
COPY main.py ./
COPY destination_firebolt ./destination_firebolt

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python3", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/destination-firebolt
