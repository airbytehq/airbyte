FROM python:3.9.11-alpine3.15 as base

# alwyays update dependencies
RUN apk update && apk upgrade -a

FROM base as builder

# upgrade pip and install libs
RUN apk --no-cache upgrade \
    && pip install --upgrade pip \
    && apk --no-cache add tzdata build-base bash

WORKDIR /airbyte/integration_code
COPY setup.py ./
RUN pip install --prefix=/install .

FROM base
WORKDIR /airbyte/integration_code
COPY --from=builder /install /usr/local

COPY main.py ./
COPY source_file ./source_file


ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.2.33
LABEL io.airbyte.name=airbyte/source-file
