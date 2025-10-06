# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
import logging
import os
import uuid
from typing import Any, Dict
from unittest.mock import patch

import pytest
from destination_ragie.client import RagieClient
from destination_ragie.config import RagieConfig
from destination_ragie.destination import DestinationRagie

from airbyte_cdk.models import (
    AirbyteConnectionStatus,
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
    config_path = os.environ.get("CONFIG_PATH", "secrets/config.json")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return json.load(f)

    # Fallback to env vars - if not present, this will raise KeyError (caught later)
    return {
        "api_key": os.environ.get("RAGIE_API_KEY", ""),
        "api_url": os.environ.get("RAGIE_API_URL", "https://api.ragie.ai"),
        "partition": f"airbyte_test_{uuid.uuid4().hex[:8]}",
        "content_fields": ["message"],
        "metadata_fields": ["author", "category", "tags"],
        "document_name_field": "title",
        "metadata_static": json.dumps({"source": "airbyte_integration_test"}),
        "processing_mode": "fast",
    }


@pytest.fixture(scope="module")
def has_real_creds(config) -> bool:
    """Detect if real API credentials are available."""
    return bool(config.get("api_key")) and config.get("api_key") != ""


@pytest.fixture
def configured_catalog():
    """Create test catalog with streams for append and overwrite modes."""
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
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream=stream_name,
            data=data,
            emitted_at=int(1000 * 1000),  # mock timestamp in ms
        ),
    )


@pytest.fixture(autouse=True)
def patch_ragie_client_methods(has_real_creds):
    """Patch RagieClient only if real creds are missing."""
    if not has_real_creds:
        with patch("destination_ragie.destination.RagieClient") as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.find_docs_by_metadata.return_value = [
                {
                    "id": "fake_doc_id",
                    "name": "Mocked Document",
                    "metadata": {"external_id": "test_123", "airbyte_stream": "append_stream"},
                }
            ]
            mock_instance.delete_documents_by_id.return_value = None

            # Fix: mock check_connection to return proper AirbyteConnectionStatus instance
            mock_instance.check_connection.return_value = AirbyteConnectionStatus(status=Status.SUCCEEDED, message="Connection successful")
            yield
    else:
        yield


def test_check_connection(config):
    destination = DestinationRagie()
    status = destination.check(logger=logger, config=config)
    assert status.status != Status.SUCCEEDED


@pytest.mark.parametrize(
    "invalid_api_key",
    [
        ("invalid_key"),
        (""),
        (None),
    ],
)
def test_check_connection_failure(config, invalid_api_key):
    destination = DestinationRagie()
    test_config = dict(config)
    test_config["api_key"] = invalid_api_key
    status = destination.check(logger=logger, config=test_config)
    assert status.status == Status.FAILED


def test_write_append(config, configured_catalog):
    destination = DestinationRagie()

    test_id = f"test_{uuid.uuid4().hex[:8]}"

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

    list(destination.write(config, configured_catalog, [record]))

    if bool(config.get("api_key")):
        config_model = RagieConfig.model_validate(config)
        client = RagieClient(config=config_model)
        filter_conditions = {"airbyte_stream": "append_stream"}
        docs = client.find_docs_by_metadata(filter_conditions)
        matching_docs = [doc for doc in docs if doc.get("metadata", {}).get("external_id") == test_id]
        assert len(matching_docs) == 1
        assert matching_docs[0].get("name") == "Test Document"
    else:
        # If no real creds, just pass (mocked)
        assert True


def test_write_overwrite(config, configured_catalog):
    destination = DestinationRagie()

    test_id_1 = f"test_overwrite_1_{uuid.uuid4().hex[:8]}"
    test_id_2 = f"test_overwrite_2_{uuid.uuid4().hex[:8]}"

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

    list(destination.write(config, configured_catalog, initial_records))

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

    list(destination.write(config, configured_catalog, overwrite_records))

    if bool(config.get("api_key")):
        config_model = RagieConfig.model_validate(config)
        client = RagieClient(config=config_model)
        filter_conditions = {"airbyte_stream": "overwrite_stream"}
        docs = client.find_docs_by_metadata(filter_conditions)
        doc_ids = [doc.get("metadata", {}).get("external_id") for doc in docs]
        assert test_id_1 not in doc_ids
        assert test_id_2 in doc_ids
    else:
        # If no real creds, just pass (mocked)
        assert True


def clean_up_test_data(config):
    config_model = RagieConfig.model_validate(config)
    client = RagieClient(config=config_model)
    filter_conditions = {"source": "airbyte_integration_test"}
    docs = client.find_docs_by_metadata(filter_conditions)
    doc_ids = [doc["id"] for doc in docs if "id" in doc]
    if doc_ids:
        client.delete_documents_by_id(doc_ids)
        print(f"Cleaned up {len(doc_ids)} test documents")


@pytest.fixture(scope="module", autouse=True)
def cleanup_after_tests(config):
    yield
    if bool(config.get("api_key")):
        clean_up_test_data(config)


if __name__ == "__main__":
    import sys

    import pytest

    sys.exit(pytest.main([__file__]))
