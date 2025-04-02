#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import io
import json
import os
import sys
import tempfile

import pytest
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
    Type,
)
from schema_generator.configure_catalog import configure_catalog
from schema_generator.infer_schemas import infer_schemas


def test_configure_catalog():
    stream = AirbyteStream(name="stream", supported_sync_modes=[SyncMode.full_refresh], json_schema={})
    catalog = AirbyteCatalog(streams=[stream])
    catalog_dict = {"type": "CATALOG", "catalog": {"streams": [{"name": "stream", "supported_sync_modes": ["full_refresh"], "json_schema": {}}]}}
    sys.stdin = io.StringIO(json.dumps(catalog_dict))

    expected_configured_catalog_json = {
        "streams": [
            {
                "stream": {
                    "name": "stream",
                    "supported_sync_modes": ["full_refresh"],
                    "json_schema": {}
                },
                "sync_mode": "full_refresh",
                "destination_sync_mode": "append"
            }
        ]
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        configure_catalog()
        assert os.path.exists("integration_tests/configured_catalog.json")

        with open("integration_tests/configured_catalog.json") as f:
            configured_catalog_json = json.loads(f.read())
            assert configured_catalog_json == expected_configured_catalog_json


def test_infer_schemas():
    expected_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "properties": {"a": {"type": "integer"}, "b": {"type": "string"}},
        "type": "object",
        "additionalProperties": True,
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        record = {"a": 1, "b": "test"}
        record_message = json.dumps({"type": "RECORD", "record": {"stream": "stream", "data": record, "emitted_at": 111}})
        sys.stdin = io.StringIO(record_message)
        infer_schemas()
        assert os.path.exists("schemas/stream.json")

        with open("schemas/stream.json") as f:
            schema = json.loads(f.read())
            assert schema == expected_schema
