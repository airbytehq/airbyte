import io
import sys
import tempfile
import os
import json

import pytest

from schema_generator.configure_catalog import configure_catalog
from schema_generator.infer_schemas import infer_schemas

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteCatalog,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
    Type,
)


def test_configure_catalog():
    stream = AirbyteStream(name="stream", supported_sync_modes=[SyncMode.full_refresh], json_schema={})
    catalog = AirbyteCatalog(streams=[stream])
    catalog_message = AirbyteMessage(type=Type.CATALOG, catalog=catalog)
    sys.stdin = io.StringIO(catalog_message.json())

    expected_configured_catalog = ConfiguredAirbyteCatalog(
        streams=[ConfiguredAirbyteStream(stream=stream, sync_mode=SyncMode.full_refresh, destination_sync_mode=DestinationSyncMode.append)]
    )

    expected_configured_catalog_json = json.loads(expected_configured_catalog.json())

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        configure_catalog()
        assert os.path.exists("integration_tests/configured_catalog.json")

        with open("integration_tests/configured_catalog.json") as f:
            configured_catalog_json = json.loads(f.read())
            assert configured_catalog_json == expected_configured_catalog_json


def test_infer_schemas():
    expected_schema = {
        "$schema": "http://json-schema.org/schema#",
        "properties": {"a": {"type": "integer"}, "b": {"type": "string"}},
        "type": "object",
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        record = {"a": 1, "b": "test"}
        record_message = AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="stream", data=record, emitted_at=111)).json()
        sys.stdin = io.StringIO(record_message)
        infer_schemas()
        assert os.path.exists("schemas/stream.json")

        with open("schemas/stream.json") as f:
            schema = json.loads(f.read())
            assert schema == expected_schema
