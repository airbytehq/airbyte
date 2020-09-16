FROM python:3.7-alpine

RUN apk add --no-cache bash

WORKDIR /singer

ENV VIRTUAL_ENV=/singer/env
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY dataline_entrypoint.py .

LABEL io.dataline.version=0.1.0
