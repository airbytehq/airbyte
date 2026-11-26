# Copyright (c) 2026 Albert Wong
# SPDX-License-Identifier: MIT
import os

import pytest
from source_redis_adbc.source import SourceRedisAdbc

from airbyte_cdk.models import ConfiguredAirbyteCatalogSerializer, Status


@pytest.mark.integration
def test_reference_flight_sql_server():
    uri = os.environ.get("FLIGHT_SQL_URI")
    if not uri:
        pytest.skip("Set FLIGHT_SQL_URI to the Apache Arrow Go SQLite reference Flight SQL server")
    config = {"uri": uri, "connection_type": "flight_sql", "schemas": [""]}
    source = SourceRedisAdbc()
    assert source.check(None, config).status == Status.SUCCEEDED
    catalog = source.discover(None, config)
    stream = next(s for s in catalog.streams if s.name == "intTable")
    selected = {name: stream.json_schema["properties"][name] for name in ("id", "keyName")}
    configured = ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {
                        "name": stream.name,
                        "namespace": stream.namespace,
                        "json_schema": {"type": "object", "properties": selected},
                        "supported_sync_modes": ["full_refresh"],
                    },
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "overwrite",
                }
            ]
        }
    )
    rows = [message.record.data for message in source.read(None, config, configured)]
    assert sorted(rows, key=lambda row: row["id"]) == [
        {"id": "1", "keyName": "one"},
        {"id": "2", "keyName": "zero"},
        {"id": "3", "keyName": "negative one"},
        {"id": "4", "keyName": None},
    ]
