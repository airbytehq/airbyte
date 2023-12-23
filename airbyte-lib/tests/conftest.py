"""Global pytest fixtures."""

import pytest
import docker
import time
from airbyte_lib.caches import PostgresCacheConfig
import os
import signal
import socket
import pytest

PYTEST_POSTGRES_CONTAINER="postgres_pytest_container"
PYTEST_POSTGRES_PORT=5432


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


@pytest.fixture(scope='session', autouse=True)
def remove_postgres_container():
    client = docker.from_env()
    if is_port_in_use(PYTEST_POSTGRES_PORT):
        try:
            container = client.containers.get(
                PYTEST_POSTGRES_CONTAINER,
            )
            container.stop()
            container.remove()
        except docker.errors.NotFound:
            pass  # Container not found, nothing to do.


@pytest.fixture(scope='session')
def pg_dsn():
    client = docker.from_env()
    postgres = client.containers.run(
        'postgres:13',
        name=PYTEST_POSTGRES_CONTAINER,
        environment={
            'POSTGRES_USER': 'postgres',
            'POSTGRES_PASSWORD': 'postgres',
            'POSTGRES_DB': 'postgres'
        },
        ports={'5432/tcp': PYTEST_POSTGRES_PORT},
        detach=True,
    )
    # Wait for the database to start
    time.sleep(5)
    url = "postgresql://postgres:postgres@localhost:5432/postgres"
    yield url
    # Stop and remove the container after the tests are done
    postgres.stop()
    postgres.remove()

@pytest.fixture
def new_pg_cache_config(pg_dsn):
    config = PostgresCacheConfig(
        host="localhost",
        port=PYTEST_POSTGRES_PORT,
        username="postgres",
        password="postgres",
        database="postgres",
        schema_name="public",
    )
    yield config
