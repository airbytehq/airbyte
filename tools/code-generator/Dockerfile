FROM python:3.10-slim
RUN pip install black==21.12b0 datamodel-code-generator==0.10.1
ENTRYPOINT ["datamodel-codegen"]

LABEL io.airbyte.version=dev
LABEL io.airbyte.name=airbyte/code-generator
