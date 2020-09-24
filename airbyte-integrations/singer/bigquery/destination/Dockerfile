FROM python:3.7-alpine

WORKDIR /singer

ENV VIRTUAL_ENV=/singer/env
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    jq \
    bash \
    curl

RUN curl -sSL https://sdk.cloud.google.com | bash
ENV PATH $PATH:/root/google-cloud-sdk/bin

# Install dependencies:
COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
  pip install -r requirements.txt

COPY entrypoint.sh /singer/entrypoint.sh

ENTRYPOINT ["sh", "/singer/entrypoint.sh"]

LABEL io.airbyte.version=0.1.3
