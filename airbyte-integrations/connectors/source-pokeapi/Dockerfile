FROM python:3.9-slim

# Bash is installed for more convenient debugging.
#RUN apt-get clean && apt-get update && apt-get install -y bash --allow-insecure-repositories && rm -rf /var/lib/apt/lists/*


WORKDIR /airbyte/integration_code
COPY src/source_pokeapi ./src/source_pokeapi
COPY main.py ./
COPY pyproject.toml ./
RUN pip install .

ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=0.1.5
LABEL io.airbyte.name=airbyte/source-pokeapi
