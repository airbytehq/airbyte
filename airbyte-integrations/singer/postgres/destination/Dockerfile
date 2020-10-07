FROM python:3.7-slim

WORKDIR /singer

ENV VIRTUAL_ENV=/singer/env
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies:
COPY requirements.txt .
COPY ./run.sh .
COPY ./src/test-integration/resources/spec.json .
COPY ./check_connection.py .

RUN apt-get update && \
  # https://github.com/datamill-co/target-postgres/issues/186
  # Need to install libpq and gcc since they're not listed in pip requirements
  apt-get -y install libpq5=11.9-0+deb10u1 && \
  apt-get -y install libpq-dev=11.9-0+deb10u1 && \
  apt-get -y install gcc=4:8.3.0-1 && \
  python -m pip install --upgrade pip && \
  pip install -r requirements.txt

ENTRYPOINT ["/singer/run.sh"]

LABEL io.airbyte.version=0.1.2
