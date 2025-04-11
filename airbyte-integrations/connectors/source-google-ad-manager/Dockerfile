FROM airbyte/python-connector-base:2.0.0

# Imposta la directory di lavoro
WORKDIR /airbyte/integration_code

# Copia dei file necessari
COPY pyproject.toml ./
COPY poetry.lock ./
COPY main.py ./
COPY README.md ./
COPY source_google_ad_manager ./source_google_ad_manager
COPY metadata.yaml ./

# Installazione di Poetry e delle dipendenze
RUN pip install --no-cache-dir poetry==1.8.3 && \
    poetry config virtualenvs.create false && \
    poetry install --without dev && \
    pip cache purge && \
    poetry cache clear pypi --all

# Etichette per il connettore
LABEL io.airbyte.name=airbyte/source_google_ad_manager
LABEL io.airbyte.version=2.0.0

# Impostazione dell'entrypoint
ENV AIRBYTE_ENTRYPOINT="python /airbyte/integration_code/main.py"
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]
