FROM python:3.11 AS base

# build and load all requirements
FROM base AS builder
WORKDIR /airbyte/integration_code

# upgrade pip to the latest version
RUN apt-get update && apt-get -y upgrade \
    && pip install --upgrade pip

COPY pyproject.toml ./
COPY README.md ./
COPY main.py ./
COPY destination_lime_crm ./destination_lime_crm


# install necessary packages to a temporary folder
RUN ls -l
RUN pip install -v --prefix=/install .

# build a clean environment
FROM base
WORKDIR /airbyte/integration_code

# # copy all loaded and built libraries to a pure basic image
COPY --from=builder /install /usr/local
# # add default timezone settings
COPY --from=builder /usr/share/zoneinfo/Etc/UTC /etc/localtime
RUN echo "Etc/UTC" > /etc/timezone

COPY main.py ./

ENV AIRBYTE_ENTRYPOINT="python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/destination_lime_crm
