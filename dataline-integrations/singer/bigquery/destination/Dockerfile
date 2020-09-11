FROM python:3.7-alpine

LABEL io.dataline.version=1.0.0

WORKDIR /singer

ENV VIRTUAL_ENV=/singer/env
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apk add --no-cache gcc musl-dev libffi-dev jq

# Install dependencies:
COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
  pip install -r requirements.txt

COPY bigquery-destination.sh /singer/bigquery-destination.sh

ENTRYPOINT ["sh", "/singer/bigquery-destination.sh"]
