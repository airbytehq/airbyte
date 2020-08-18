FROM python:3.7-slim

WORKDIR /singer

ENV VIRTUAL_ENV=/singer/env
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# need gcc to compile psycopg2
#RUN apt-get update && \
#  apt-get install -y libpq-dev gcc

# Install dependencies:
COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
  pip install -r requirements.txt

#RUN apt-get autoremove -y gcc

ENTRYPOINT ["target-postgres"]
