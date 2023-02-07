ARG PYTHON_VERSION=3.9.13-alpine3.15
FROM python:${PYTHON_VERSION}

# alwyays update dependencies
RUN apk update && apk upgrade -a

# install deps
RUN apk --no-cache add bash tzdata build-base

# upgrade pip to the latest version
RUN pip install --upgrade pip

# add default timezone settings
ENV TZ="Etc/UTC"

LABEL io.airbyte.version=0.0.1
LABEL io.airbyte.name=airbyte/integration-base-python
