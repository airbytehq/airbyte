FROM python:3.7-slim

WORKDIR /singer

ENV VIRTUAL_ENV=/singer/env
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apt-get update && apt-get install -y jq

# Install dependencies:
COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
  pip install -r requirements.txt

COPY entrypoint.sh .

ENTRYPOINT ["/singer/entrypoint.sh"]

LABEL io.dataline.version=0.1.0
