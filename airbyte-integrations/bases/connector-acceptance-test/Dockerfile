FROM python:3.10.12 as builder
RUN apt-get update \
    && pip install --upgrade pip \
    && apt-get install tzdata

RUN pip install poetry==1.5.1
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache


WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

FROM python:3.10.12 as runtime

COPY --from=builder /usr/share/zoneinfo/Etc/UTC /etc/localtime
ENV ACCEPTANCE_TEST_DOCKER_CONTAINER 1
RUN echo "Etc/UTC" > /etc/timezone

# Bash is installed for more convenient debugging.
RUN apt-get install bash curl
ENV DOCKER_VERSION = "24.0.2"
RUN curl -fsSL https://get.docker.com | sh

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY connector_acceptance_test ./connector_acceptance_test

ENTRYPOINT ["python", "-m", "pytest", "-p", "connector_acceptance_test.plugin", "-r", "fEsx", "--show-capture=log"]
