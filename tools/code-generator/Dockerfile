FROM python:3.11.0b5-alpine3.15 as base
FROM base as builder


RUN apk --no-cache upgrade \
    && pip install --upgrade pip  \
    && apk add  g++ make

# the new version (>= 2.1.0) of package markupsafe removed the funcion `soft_unicode`. And it broke other dependences
# https://github.com/pallets/markupsafe/blob/main/CHANGES.rst
# thus this version is pinned
# RUN  pip install --prefix=/install markupsafe==2.0.1
RUN  pip install --prefix=/install black==22.1.0 datamodel_code_generator==0.11.19

FROM base
COPY --from=builder /install /usr/local

ENTRYPOINT ["datamodel-codegen"]

LABEL io.airbyte.version=dev
LABEL io.airbyte.name=airbyte/code-generator
