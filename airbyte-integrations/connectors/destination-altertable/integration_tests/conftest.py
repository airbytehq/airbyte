# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import os
import uuid
from typing import Generator

import altertable_flightsql
import pytest
from destination_altertable.destination import DestinationAltertable
from testcontainers.core.container import DockerContainer, LogMessageWaitStrategy


ALTERTABLE_MOCK_IMAGE = "ghcr.io/altertable-ai/altertable-mock"
ALTERTABLE_MOCK_PORT = 15002


class AltertableContainer(DockerContainer):
    """Testcontainer for Altertable mock service."""

    def __init__(
        self,
        image: str = "ghcr.io/altertable-ai/altertable-mock:sha-a0875ff",
        port: int = 15002,
    ):
        super().__init__(image)
        self.port = port
        self.with_exposed_ports(port)
        self.with_env("ALTERTABLE_MOCK_FLIGHT_PORT", str(port))
        self.with_env("ALTERTABLE_MOCK_USERS", "altertable-test:lk_test")
        self.waiting_for(LogMessageWaitStrategy("Starting Flight SQL server on"))

    def get_connection_params(self) -> dict:
        """Get connection parameters for the container."""
        return {
            "host": self.get_container_host_ip(),
            "port": int(self.get_exposed_port(self.port)),
            "username": "altertable-test",
            "password": "lk_test",
            "tls": False,
            "catalog": None,
            "schema": None,
        }


@pytest.fixture(scope="session")
def altertable_service() -> Generator[dict, None, None]:
    """
    Provide Altertable service connection parameters.

    This fixture checks for environment variables to determine if an existing
    service is available. If not, it starts a testcontainer.

    Environment variables:
        ALTERTABLE_HOST: Hostname of existing service
        ALTERTABLE_PORT: Port of existing service
        ALTERTABLE_USERNAME: Username for authentication
        ALTERTABLE_PASSWORD: Password for authentication
        ALTERTABLE_CATALOG: Catalog for the connection
        ALTERTABLE_SCHEMA: Schema for the connection

    Yields:
        dict: Connection parameters (host, port, username, password, tls)
    """
    host = os.getenv("ALTERTABLE_HOST")
    port = os.getenv("ALTERTABLE_PORT")
    username = os.getenv("ALTERTABLE_USERNAME")
    password = os.getenv("ALTERTABLE_PASSWORD")
    catalog = os.getenv("ALTERTABLE_CATALOG")
    schema = os.getenv("ALTERTABLE_SCHEMA")
    tls = os.getenv("ALTERTABLE_TLS", "true").lower() == "true"

    if host and port:
        # Use existing service
        yield {
            "host": host,
            "port": int(port),
            "username": username,
            "password": password,
            "tls": tls,
            "catalog": catalog,
            "schema": schema,
        }
    else:
        with AltertableContainer() as container:
            print(container.get_logs())
            yield container.get_connection_params()


@pytest.fixture
def destination() -> Generator[DestinationAltertable, None, None]:
    """
    Provide an Altertable destination.
    """
    yield DestinationAltertable()


@pytest.fixture
def client(
    altertable_service: dict,
) -> Generator[altertable_flightsql.Client, None, None]:
    """
    Provide an Altertable client connected to the test service.

    This fixture creates a fresh client for each test and ensures proper cleanup.

    Args:
        altertable_service: Service connection parameters from fixture

    Yields:
        Client: Connected Altertable client
    """
    with altertable_flightsql.Client(**altertable_service) as client:
        yield client


@pytest.fixture
def data(client: altertable_flightsql.Client):
    catalog_name = f"catalog_{uuid.uuid4().hex[:8]}"
    schema_name = f"schema_{uuid.uuid4().hex[:8]}"
    test_table_name = f"table_{uuid.uuid4().hex[:8]}"

    client.execute(f"ATTACH ':memory:' AS {catalog_name}")
    client.execute(f"CREATE SCHEMA IF NOT EXISTS {catalog_name}.{schema_name}")
    client.execute(f"""
        CREATE TABLE IF NOT EXISTS {catalog_name}.{schema_name}.{test_table_name} 
            (id INT, name STRING, created_at TIMESTAMP)
    """)
    client.execute(f"""
        INSERT INTO {catalog_name}.{schema_name}.{test_table_name} (id, name, created_at) 
            VALUES 
                (1, 'John Doe', '2021-01-01 12:00:00'), 
                (2, 'Jane Doe', '2021-01-01 12:00:00'), 
                (3, 'Jim Doe', '2021-01-01 12:00:00')
    """)

    yield catalog_name, schema_name, test_table_name

    client.execute(f"DROP TABLE IF EXISTS {catalog_name}.{schema_name}.{test_table_name}")
    client.execute(f"DROP SCHEMA IF EXISTS {catalog_name}.{schema_name}")
    client.execute(f"DETACH {catalog_name}")
