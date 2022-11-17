FROM python:3.10-slim@sha256:13b98a4ddf43c98e3f91bd5136844ff0b0c1d2a4c913b4a430d552a43d4c7b3b as base

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
COPY source_kapiche_export_api ./source_kapiche_export_api

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/source-kapiche-export-api
