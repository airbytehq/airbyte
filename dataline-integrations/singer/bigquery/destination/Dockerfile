FROM python:3.7-alpine

WORKDIR /singer

ENV VIRTUAL_ENV=/singer/env
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apk add --no-cache gcc musl-dev libffi-dev

# Install dependencies:
COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
  pip install -r requirements.txt

WORKDIR /singer/data

COPY bigquery-target.sh .

ENTRYPOINT ["sh", "target-bigquery.sh"]
