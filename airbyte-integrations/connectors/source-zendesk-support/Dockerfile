FROM python:3.9.11-alpine3.15 as base
FROM base as builder


RUN apk --no-cache upgrade \
    && pip install --upgrade pip  \
    && apk --no-cache add tzdata build-base

WORKDIR /airbyte/integration_code
COPY setup.py ./
RUN pip install --prefix=/install .


FROM base
COPY --from=builder /install /usr/local
# add default timezone settings
COPY --from=builder /usr/share/zoneinfo/Etc/UTC /etc/localtime
RUN echo "Etc/UTC" > /etc/timezone

WORKDIR /airbyte/integration_code
COPY main.py ./
COPY source_zendesk_support ./source_zendesk_support


ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.7.0
LABEL io.airbyte.name=airbyte/source-zendesk-support
