# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""Global pytest fixtures."""

import json
import logging
import os
import socket
import time
from typing import Optional
from airbyte_lib.caches.snowflake import SnowflakeCacheConfig

import docker
import psycopg
import pytest
from google.cloud import secretmanager

from airbyte_lib.caches import PostgresCacheConfig

logger = logging.getLogger(__name__)


PYTEST_POSTGRES_IMAGE = "postgres:13"
PYTEST_POSTGRES_CONTAINER = "postgres_pytest_container"
PYTEST_POSTGRES_PORT = 5432


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


@pytest.fixture(scope="session", autouse=True)
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


def test_pg_connection(host) -> bool:
    pg_url = f"postgresql://postgres:postgres@{host}:{PYTEST_POSTGRES_PORT}/postgres"

    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            conn = psycopg.connect(pg_url)
            conn.close()
            return True
        except psycopg.OperationalError:
            logger.info(f"Waiting for postgres to start (attempt {attempt + 1}/{max_attempts})")
            time.sleep(1.0)

    else:
        return False


@pytest.fixture(scope="session")
def pg_dsn():
    client = docker.from_env()
    try:
        client.images.get(PYTEST_POSTGRES_IMAGE)
    except docker.errors.ImageNotFound:
        # Pull the image if it doesn't exist, to avoid failing our sleep timer
        # if the image needs to download on-demand.
        client.images.pull(PYTEST_POSTGRES_IMAGE)

    postgres = client.containers.run(
        image=PYTEST_POSTGRES_IMAGE,
        name=PYTEST_POSTGRES_CONTAINER,
        environment={"POSTGRES_USER": "postgres", "POSTGRES_PASSWORD": "postgres", "POSTGRES_DB": "postgres"},
        ports={"5432/tcp": PYTEST_POSTGRES_PORT},
        detach=True,
    )
    time.sleep(0.5)

    final_host = None
    # Try to connect to the database using localhost and the docker host IP
    for host in ["localhost", "172.17.0.1"]:
        if test_pg_connection(host):
            final_host = host
            break
    else:
        raise Exception("Failed to connect to the PostgreSQL database.")

    yield final_host
    # Stop and remove the container after the tests are done
    postgres.stop()
    postgres.remove()


@pytest.fixture
def new_pg_cache_config(pg_dsn):
    config = PostgresCacheConfig(
        host=pg_dsn,
        port=PYTEST_POSTGRES_PORT,
        username="postgres",
        password="postgres",
        database="postgres",
        schema_name="public",
    )
    yield config

@pytest.fixture
def snowflake_config():
    if "GCP_GSM_CREDENTIALS" not in os.environ:
        raise Exception("GCP_GSM_CREDENTIALS env variable not set, can't fetch secrets for Snowflake. Make sure they are set up as described: https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/ci_credentials/README.md#get-gsm-access")
    secret_client = secretmanager.SecretManagerServiceClient.from_service_account_info(
        json.loads(os.environ["GCP_GSM_CREDENTIALS"])
    )
    secret = json.loads(
        secret_client.access_secret_version(
            name="projects/dataline-integration-testing/secrets/AIRBYTE_LIB_SNOWFLAKE_CREDS/versions/latest"
        ).payload.data.decode("UTF-8")
    )
    config = SnowflakeCacheConfig(
        account=secret["account"],
        username=secret["username"],
        password=secret["password"],
        database=secret["database"],
        warehouse=secret["warehouse"],
        role=secret["role"],
    )

    yield config
