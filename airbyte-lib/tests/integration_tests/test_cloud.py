"""Cloud integration tests."""

import os
import pytest
from airbyte_lib.caches.duckdb import DuckDBCache

from airbyte_lib.cloud import (
    CloudRunResult,
    HostedAirbyteResource,
    HostedConnection,
    HostedDestination,
    HostedSource,
    get_cloud_connection,
    AirbyteCloud,
)
from airbyte_lib import (
    Source,
    Destination,
    new_local_cache,
    get_connector,
)

AIRBYTE_API_ROOT = "https://www.airbyte.io"


@pytest.fixture
def cloud_api_root() -> str:
    """Return the Airbyte API root."""
    return AIRBYTE_API_ROOT

@pytest.fixture
def cloud_api_key() -> str:
    """Return the Airbyte API root."""
    return os.environ.get("AIRBYTE_API_KEY", None)

@pytest.fixture
def connection_id() -> str:
    """Return a connection ID."""
    return "123"

@pytest.fixture
def workspace_id() -> str:
    """Return a connection ID."""
    return "123"

@pytest.fixture
def faker_source() -> Source:
    """Return a source object for the Faker source."""
    return get_connector(
        name="source-faker",
    )

def test_get_cloud_connection(connection_id: str) -> None:
    """Test get_cloud_connection."""
    conn: HostedConnection = get_cloud_connection(
        workspace_id="123",
        connection_id="456",
        api_key="789",
        api_root=AIRBYTE_API_ROOT,
    )

def test_create_and_run_cloud_connection(
    workspace_id: str,
    cloud_api_root: str,
    cloud_api_key: str,
    faker_source: Source,
) -> None:
    """Test create_source."""
    cache: DuckDBCache = new_local_cache()
    airbyte_instance = AirbyteCloud()

    hosted_source: HostedSource = airbyte_instance.create_or_replace_source(
        source=faker_source,

        workspace_id=workspace_id,
        api_root=cloud_api_root,
        api_key=cloud_api_key,
    )
    hosted_destination: HostedDestination = create_cache_as_cloud_destination(
        cache=cache,
        workspace_id=workspace_id,
        api_root=cloud_api_root,
        api_key=cloud_api_key,
    )
    hosted_connection: HostedConnection = create_connection_in_cloud(
        hosted_source=hosted_source,
        hosted_destination=hosted_destination,
        workspace_id=workspace_id,
        api_root=cloud_api_root,
        api_key=cloud_api_key,
    )
    run_result: CloudRunResult = hosted_connection.run()
