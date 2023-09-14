# ---------------------------------------------------------------------------- #
#                                 general args                                 #
# ---------------------------------------------------------------------------- #

ARG WORKDIR=/airbyte/integration_code

# ---------------------------------------------------------------------------- #
#                                 builder stage                                #
# ---------------------------------------------------------------------------- #


FROM python:3.10-slim AS builder

# Bash is installed for more convenient debugging.
# RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*

# refresh workdir
ARG WORKDIR

# Poetry version
ARG POETRY_VERSION=1.5.1

# Pipx version
ARG PIPX_VERSION=1.2.0

ENV PATH=/opt/pipx/bin:${WORKDIR}/.venv/bin:$PATH \
	PIPX_BIN_DIR=/opt/pipx/bin \
	PIPX_HOME=/opt/pipx/home \
	PIPX_VERSION=$PIPX_VERSION \
	POETRY_VERSION=$POETRY_VERSION \
	PYTHONPATH=${WORKDIR} \
	# Don't buffer `stdout`
	PYTHONUNBUFFERED=1 \
	# Don't create `.pyc` files:
	PYTHONDONTWRITEBYTECODE=1 \
	# make poetry create a .venv folder in the project
	POETRY_VIRTUALENVS_IN_PROJECT=true

# Install Pipx using pip
RUN python -m pip install --no-cache-dir --upgrade pip pipx==${PIPX_VERSION}
RUN pipx ensurepath && pipx --version

# Set working directory
WORKDIR ${WORKDIR}

# Install Poetry using pipx
RUN pipx install --force poetry==${POETRY_VERSION}

# copy only requirements to cache them in docker layer
COPY pyproject.toml poetry.lock ./

# install dependencies
RUN poetry install --only main

# copy rest of files
COPY source_sftp_bulk ./source_sftp_bulk
COPY main.py ./


# ---------------------------------------------------------------------------- #
#                                  final stage                                 #
# ---------------------------------------------------------------------------- #

FROM python:3.10-slim AS final

ARG WORKDIR

ENV PATH=${WORKDIR}/.venv/bin:$PATH \
	PYTHONPATH=${WORKDIR} \
	# Don't buffer `stdout`
	PYTHONUNBUFFERED=1 \
	# Don't create `.pyc` files:
	PYTHONDONTWRITEBYTECODE=1

WORKDIR ${WORKDIR}

COPY --from=builder ${WORKDIR}/ ./

ENV AIRBYTE_ENTRYPOINT="python ${WORKDIR}/main.py"

ENTRYPOINT ["python", "main.py"]

LABEL io.airbyte.version=0.1.3
LABEL io.airbyte.name=airbyte/source-sftp-bulk
