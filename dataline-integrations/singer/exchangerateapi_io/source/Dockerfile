FROM python:3.7-slim

LABEL io.dataline.version=0.1.1

WORKDIR /singer

ENV VIRTUAL_ENV=/singer/env
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies:
COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
  pip install -r requirements.txt

ENTRYPOINT ["tap-exchangeratesapi"]
