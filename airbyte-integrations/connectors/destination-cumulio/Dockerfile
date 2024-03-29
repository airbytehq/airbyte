FROM python:3.9.11 as base
# FROM python:3.9.11-alpine3.15 as base
# switched from alpine as there were tons of errors (in case you want to switch back to alpine)
# - https://stackoverflow.com/a/57485724/5246670
# - numpy error: https://stackoverflow.com/a/22411624/5246670
# - libstdc++ https://github.com/amancevice/docker-pandas/issues/12#issuecomment-717215043
# - musl-dev linux-headers g++ because of: https://stackoverflow.com/a/40407099/5246670

# build and load all requirements
FROM base as builder
WORKDIR /airbyte/integration_code

# upgrade pip to the latest version
RUN apt-get update && apt-get -y upgrade \
    && pip install --upgrade pip

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
COPY destination_cumulio ./destination_cumulio

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.1.1
LABEL io.airbyte.name=airbyte/destination-cumulio
