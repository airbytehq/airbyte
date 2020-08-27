FROM python:3.7-slim

ARG WORKDIR=/data

WORKDIR /singer

ENV VIRTUAL_ENV=/singer/env
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies:
COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
  pip install -r requirements.txt

VOLUME $WORKDIR
WORKDIR $WORKDIR
ENTRYPOINT ["target-csv"]
