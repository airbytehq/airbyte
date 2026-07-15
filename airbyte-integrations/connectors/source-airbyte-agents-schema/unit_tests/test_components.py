#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest


_COMPONENTS_PATH = Path(__file__).parent.parent / "components.py"
_spec = importlib.util.spec_from_file_location("agents_schema_components", _COMPONENTS_PATH)
components = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = components
_spec.loader.exec_module(components)


DESTINATION_ID = "dest-1111"
OTHER_DESTINATION_ID = "dest-9999"


def _connections_response():
    """A `connections` list response spanning two destinations."""
    body = {
        "data": [
            {
                "connectionId": "conn-a",
                "name": "Postgres to Warehouse",
                "workspaceId": "ws-1",
                "sourceId": "src-a",
                "destinationId": DESTINATION_ID,
                "status": "active",
                "prefix": "raw_",
                "namespaceDefinition": "source",
                "namespaceFormat": None,
                "configurations": {
                    "streams": [
                        {
                            "name": "users",
                            "namespace": "public",
                            "syncMode": "incremental_deduped_history",
                            "primaryKey": [["id"]],
                            "cursorField": ["updated_at"],
                            "selectedFields": [
                                {"fieldPath": ["id"]},
                                {"fieldPath": ["email"]},
                            ],
                        },
                        {
                            "name": "orders",
                            "namespace": "public",
                            "syncMode": "full_refresh_overwrite",
                        },
                    ]
                },
            },
            {
                "connectionId": "conn-b",
                "name": "Custom NS",
                "destinationId": DESTINATION_ID,
                "prefix": None,
                "namespaceDefinition": "custom_format",
                "namespaceFormat": "analytics_${SOURCE_NAMESPACE}",
                "configurations": {
                    "streams": [
                        {"name": "events", "namespace": "app"},
                    ]
                },
            },
            {
                "connectionId": "conn-other",
                "destinationId": OTHER_DESTINATION_ID,
                "configurations": {"streams": [{"name": "should_not_appear"}]},
            },
        ]
    }
    response = Mock()
    response.json.return_value = body
    return response


@pytest.fixture
def config():
    return {"destination_id": DESTINATION_ID, "client_id": "x", "client_secret": "y"}


def test_stream_extractor_scopes_to_destination(config):
    extractor = components.AgentsStreamExtractor(config=config)
    records = list(extractor.extract_records(_connections_response()))

    names = {r["stream_name"] for r in records}
    assert names == {"users", "orders", "events"}
    assert "should_not_appear" not in names


def test_stream_extractor_derives_table_name_and_namespace(config):
    extractor = components.AgentsStreamExtractor(config=config)
    by_name = {r["stream_name"]: r for r in extractor.extract_records(_connections_response())}

    # source namespace + prefix
    assert by_name["users"]["destination_namespace"] == "public"
    assert by_name["users"]["destination_table_name"] == "raw_users"
    assert by_name["users"]["primary_key"] == [["id"]]
    assert by_name["users"]["selected_fields"] == ["id", "email"]

    # custom_format namespace, no prefix
    assert by_name["events"]["destination_namespace"] == "analytics_app"
    assert by_name["events"]["destination_table_name"] == "events"


def test_root_extractor_emits_index_and_skill(config):
    extractor = components.AgentsRootExtractor(config=config)
    records = list(extractor.extract_records(_connections_response()))

    keys = {r["key"] for r in records}
    assert "index" in keys
    assert "skill/query-airbyte-landed-data" in keys
    assert all(r["provider"] == "airbyte" for r in records)

    index = next(r for r in records if r["key"] == "index")
    payload = json.loads(index["content"])
    assert payload["destination_id"] == DESTINATION_ID
    assert payload["extensions"] == ["AIRBYTE_STREAM"]
    # The index is response-independent: the per-stream/table inventory is a cross-page
    # aggregation that lives in `airbyte_stream`, not summarized here.
    assert "tables" not in payload
    assert "connection_count" not in payload
    assert "stream_count" not in payload
