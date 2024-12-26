FROM python:3.11-slim

# Bash is installed for more convenient debugging.
RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*

WORKDIR /airbyte/integration_code
COPY poetry.lock pyproject.toml ./

# Install poetry and dependencies
RUN pip install poetry==1.7.1 \
    && poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi

# Copy the rest of the code
COPY . .

# Make sure the entrypoint is executable
RUN chmod +x main.py

ENV AIRBYTE_ENTRYPOINT="python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/source-pulse-google-directory