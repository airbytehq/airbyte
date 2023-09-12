FROM python:3.9.18-bookworm@sha256:0d132e30eb9325d53c790738e5478e9abffc98b69115e7de429d7c6fc52dddac
ENV AIRBYTE_BASE_BASE_IMAGE=python:3.9.18-bookworm@sha256:0d132e30eb9325d53c790738e5478e9abffc98b69115e7de429d7c6fc52dddac
ENV AIRBYTE_BASE_IMAGE=airbyte-python-connector-base:1.0.0
LABEL io.airbyte.base_base_image=python:3.9.18-bookworm@sha256:0d132e30eb9325d53c790738e5478e9abffc98b69115e7de429d7c6fc52dddac
LABEL io.airbyte.base_image=airbyte-python-connector-base:1.0.0
RUN ln -snf /usr/share/zoneinfo/Etc/UTC /etc/localtime
RUN pip install --upgrade pip==23.2.1