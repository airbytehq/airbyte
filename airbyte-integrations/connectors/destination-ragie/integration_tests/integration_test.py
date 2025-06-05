#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#
import json
import logging
import os
import uuid
from typing import Any, Dict

import pytest
from .destination_ragie.client import RagieClient
from .destination_ragie.config import RagieConfig
from .destination_ragie.destination import DestinationRagie

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    Status,
    SyncMode,
    Type,
)


logging.basicConfig(level=logging.INFO)


logger = logging.getLogger("airbyte.integration_tests.ragie")


@pytest.fixture(scope="module")
def config() -> Dict[str, Any]:
    """Fixture to load test configuration from environment variables or config file."""
    # First try to load from environment
    config_path = os.environ.get("CONFIG_PATH", "secrets/config.json")

    # Default to loading from config file if variable not set
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return json.load(f)

    # Use environment variables as fallback
    return {
        "api_key": os.environ["RAGIE_API_KEY"],
        "api_url": os.environ.get("RAGIE_API_URL", "https://api.ragie.ai"),
        "partition": f"airbyte_test_{uuid.uuid4().hex[:8]}",  # Use unique partition for isolation
        "content_fields": ["message"],
        "metadata_fields": ["author", "category", "tags"],
        "document_name_field": "title",
        "metadata_static": json.dumps({"source": "airbyte_integration_test"}),
        "processing_mode": "fast",
    }


@pytest.fixture
def configured_catalog():
    """Create test catalog with streams for both append and overwrite modes."""
    append_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name="append_stream",
            json_schema={"type": "object"},
            supported_sync_modes=[SyncMode.incremental],
        ),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
    )

    overwrite_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name="overwrite_stream",
            json_schema={"type": "object"},
            supported_sync_modes=[SyncMode.full_refresh],
        ),
        sync_mode=SyncMode.full_refresh,
        destination_sync_mode=DestinationSyncMode.overwrite,
    )

    return ConfiguredAirbyteCatalog(streams=[append_stream, overwrite_stream])


def make_record(stream_name: str, data: Dict[str, Any]) -> AirbyteMessage:
    """Helper to create an Airbyte record message."""
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream=stream_name,
            data=data,
            emitted_at=int(1000 * 1000),  # milliseconds
        ),
    )


def test_check_connection(config):
    """Test that connection check works with valid credentials."""
    destination = DestinationRagie()
    status = destination.check(logger=logger, config=config)
    assert status.status == Status.SUCCEEDED


@pytest.mark.parametrize(
    "invalid_config,error_substring",
    [
        ({"api_key": "invalid_key"}, "Authentication failed"),
    ],
)
def test_check_connection_failure(config, invalid_config, error_substring):
    """Test connection failures with invalid credentials."""
    destination = DestinationRagie()
    test_config = {**config, **invalid_config}  # Merge configs
    status = destination.check(logger=logger, config=test_config)
    assert status.status == Status.FAILED
    assert error_substring in status.message


def test_write_append(config, configured_catalog):
    """Test writing to an append mode stream."""
    # Setup
    destination = DestinationRagie()

    # Create unique identifiers for test data
    test_id = f"test_{uuid.uuid4().hex[:8]}"

    # Create test messages
    record = make_record(
        "append_stream",
        {
            "id": test_id,
            "title": "Test Document",
            "message": "This is a test document for integration testing",
            "author": "Airbyte Test",
            "category": "Integration Test",
            "tags": ["test", "integration", "airbyte"],
        },
    )

    # Run destination with test messages
    list(destination.write(config, configured_catalog, [record]))

    # Verify data was written
    config_model = RagieConfig.model_validate(config)
    client = RagieClient(config=config_model)

    # Query by metadata to find our test record
    filter_conditions = {
        "airbyte_stream": "append_stream",
    }
    docs = client.find_docs_by_metadata(filter_conditions)

    # Verify document was created with correct content
    matching_docs = [doc for doc in docs if doc.get("metadata", {}).get("external_id") == test_id]
    assert len(matching_docs) == 1
    assert matching_docs[0].get("name") == "Test Document"


def test_write_overwrite(config, configured_catalog):
    """Test writing to an overwrite mode stream."""
    # Setup
    destination = DestinationRagie()

    # Create unique identifiers for test data
    test_id_1 = f"test_overwrite_1_{uuid.uuid4().hex[:8]}"
    test_id_2 = f"test_overwrite_2_{uuid.uuid4().hex[:8]}"

    # First batch - write initial data
    initial_records = [
        make_record(
            "overwrite_stream",
            {
                "id": test_id_1,
                "title": "Initial Document 1",
                "message": "This document should be overwritten",
                "author": "Airbyte Test",
                "category": "Integration Test",
                "tags": ["initial", "test"],
            },
        )
    ]

    # Run destination with initial records
    list(destination.write(config, configured_catalog, initial_records))

    # Second batch - this should overwrite the first batch
    overwrite_records = [
        make_record(
            "overwrite_stream",
            {
                "id": test_id_2,
                "title": "New Document",
                "message": "This is the new document after overwrite",
                "author": "Airbyte Test",
                "category": "Integration Test",
                "tags": ["overwrite", "test"],
            },
        )
    ]

    # Run destination with overwrite records
    list(destination.write(config, configured_catalog, overwrite_records))

    # Verify data was correctly overwritten
    config_model = RagieConfig.model_validate(config)
    client = RagieClient(config=config_model)

    # Query by metadata to find our test records
    filter_conditions = {
        "airbyte_stream": "overwrite_stream",
    }
    docs = client.find_docs_by_metadata(filter_conditions)

    # Check that only the new document exists
    doc_ids = [doc.get("metadata", {}).get("external_id") for doc in docs]
    assert test_id_1 not in doc_ids
    assert test_id_2 in doc_ids


def clean_up_test_data(config):
    """Helper to clean up test data after integration tests."""
    config_model = RagieConfig.model_validate(config)
    client = RagieClient(config=config_model)

    # Find all test documents by the source metadata
    filter_conditions = {"source": "airbyte_integration_test"}

    docs = client.find_docs_by_metadata(filter_conditions)
    doc_ids = [doc["id"] for doc in docs if "id" in doc]

    if doc_ids:
        client.delete_documents_by_id(doc_ids)
        print(f"Cleaned up {len(doc_ids)} test documents")


@pytest.fixture(scope="module", autouse=True)
def cleanup_after_tests(config):
    """Fixture to clean up test data after all tests have run."""
    yield  # Run all tests
    clean_up_test_data(config)


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
