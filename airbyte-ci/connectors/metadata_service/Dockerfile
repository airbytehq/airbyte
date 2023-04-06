ARG PYTHON_VERSION=3.9.11
ARG POETRY_VERSION=1.2.2
ARG POETRY_HOME=/opt/poetry

FROM python:$PYTHON_VERSION
ARG POETRY_VERSION
ARG POETRY_HOME

ENV \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1

ENV \
    POETRY_VERSION=$POETRY_VERSION \
    POETRY_HOME=$POETRY_HOME \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

# Install Poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python
ENV PATH=$POETRY_HOME/bin:$PATH

# TODO: adding tree command for testing; possibly remove?
RUN apt update && apt install tree

# Copy our project files
WORKDIR /src
COPY ./lib ./lib
COPY ./orchestrator ./orchestrator

# Set working dir to orchestrator
WORKDIR /src/orchestrator

RUN poetry install
