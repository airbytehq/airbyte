FROM python:3.7-alpine

WORKDIR /singer

ENV VIRTUAL_ENV=/singer/env
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies:
COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
  pip install -r requirements.txt

RUN apk add --no-cache jq curl bash

COPY entrypoint.sh .

ENTRYPOINT ["/singer/entrypoint.sh"]

LABEL io.dataline.version=0.1.0
