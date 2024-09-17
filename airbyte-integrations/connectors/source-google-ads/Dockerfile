FROM python:3.10-slim

# Bash is installed for more convenient debugging.
RUN apt-get update && apt-get install -y bash && apt-get install -y socat && rm -rf /var/lib/apt/lists/*

WORKDIR /airbyte/integration_code
COPY source_google_ads ./source_google_ads
COPY main.py ./main.py
COPY poetry.lock ./poetry.lock
COPY pyproject.toml ./pyproject.toml
COPY README.md ./README.md

ENV POETRY_VIRTUALENVS_CREATE=false

RUN pip install poetry
RUN poetry install

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"

ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=2.0.0
LABEL io.airbyte.name=airbyte/source-google-ads
