FROM python:3.9.11-alpine3.15 as base
FROM base as builder


RUN apk --no-cache upgrade \
    && pip install --upgrade pip

WORKDIR /airbyte/integration_code
COPY setup.py ./
RUN pip install --prefix=/install .


FROM base
COPY --from=builder /install /usr/local

WORKDIR /airbyte/integration_code
COPY main.py ./
COPY source_cart ./source_cart


ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.2.0
LABEL io.airbyte.name=airbyte/source-cart
