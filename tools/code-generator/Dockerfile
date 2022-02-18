FROM python:3.7.11-alpine3.14 as base
FROM base as builder


RUN apk --no-cache upgrade \
    && pip install --upgrade pip  \
    && apk add  g++ make

RUN  pip install --prefix=/install black==22.1.0 datamodel_code_generator==0.11.19

FROM base
COPY --from=builder /install /usr/local

ENTRYPOINT ["datamodel-codegen"]

LABEL io.airbyte.version=dev
LABEL io.airbyte.name=airbyte/code-generator
