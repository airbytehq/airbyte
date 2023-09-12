FROM python:3.9.18-bookworm@sha256:40582fe697811beb7bfceef2087416336faa990fd7e24984a7c18a86d3423d58
ENV AIRBYTE_BASE_BASE_IMAGE=python:3.9.18-bookworm@sha256:40582fe697811beb7bfceef2087416336faa990fd7e24984a7c18a86d3423d58
ENV AIRBYTE_BASE_IMAGE=airbyte-python-connector-base:1.1.1
LABEL io.airbyte.base_base_image=python:3.9.18-bookworm@sha256:40582fe697811beb7bfceef2087416336faa990fd7e24984a7c18a86d3423d58
LABEL io.airbyte.base_image=airbyte-python-connector-base:1.1.1
RUN ln -snf /usr/share/zoneinfo/Etc/UTC /etc/localtime
RUN pip install --upgrade pip==23.2.1
ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_VIRTUALENVS_IN_PROJECT=false
ENV POETRY_NO_INTERACTION=1
RUN pip install poetry==1.6.1
RUN pip install poetry==1.6.0