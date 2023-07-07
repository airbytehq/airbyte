FROM python:3.10-slim@sha256:9fa0bd93ffda9d47ef8290d05c905077298032a06cf100101981ddf483150d92 as base

# build and load all requirements
FROM base as builder
WORKDIR /airbyte/integration_code

# upgrade pip to the latest version
RUN apt-get upgrade \
    && pip install --upgrade pip --no-cache\
    && apt-get install tzdata

COPY setup.py ./
# install necessary packages to a temporary folder
RUN pip install --prefix=/install . --only-binary pandas

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
COPY source ./source

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.2.0
LABEL io.airbyte.name=airbyte/source-kapiche-rms-cloud-api
