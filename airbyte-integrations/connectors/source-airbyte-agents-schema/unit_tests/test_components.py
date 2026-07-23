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


def _connection_catalog_response():
    """A single Config API `web_backend/connections/get` response for one connection."""
    body = {
        "connectionId": "conn-a",
        "name": "Postgres to Warehouse",
        "sourceId": "src-a",
        "destinationId": DESTINATION_ID,
        "status": "active",
        "prefix": "raw_",
        "namespaceDefinition": "source",
        "namespaceFormat": None,
        "latestSyncJobStatus": "succeeded",
        "latestSyncJobCreatedAt": 1775182720,
        "isSyncing": False,
        "source": {"workspaceId": "ws-1"},
        "destination": {"workspaceId": "ws-1"},
        "syncCatalog": {
            "streams": [
                {
                    "stream": {
                        "name": "users",
                        "namespace": "public",
                        "jsonSchema": {
                            "properties": {
                                "id": {"type": "integer"},
                                "email": {"type": ["null", "string"]},
                                "note": {"type": ["null", "string"]},
                            }
                        },
                    },
                    "config": {
                        "selected": True,
                        "syncMode": "incremental",
                        "destinationSyncMode": "append_dedup",
                        "primaryKey": [["id"]],
                        "cursorField": ["updated_at"],
                        "fieldSelectionEnabled": True,
                        "selectedFields": [{"fieldPath": ["id"]}, {"fieldPath": ["email"]}],
                    },
                },
                {
                    "stream": {
                        "name": "orders",
                        "namespace": "public",
                        "jsonSchema": {"properties": {"order_id": {"type": "integer"}}},
                    },
                    "config": {
                        "selected": True,
                        "syncMode": "full_refresh",
                        "destinationSyncMode": "overwrite",
                        "fieldSelectionEnabled": False,
                        "selectedFields": [],
                    },
                },
                {
                    "stream": {"name": "unselected", "namespace": "public", "jsonSchema": {"properties": {}}},
                    "config": {"selected": False},
                },
            ]
        },
    }
    response = Mock()
    response.json.return_value = body
    return response


@pytest.fixture
def config():
    return {"destination_id": DESTINATION_ID, "client_id": "x", "client_secret": "y"}


def test_catalog_extractor_emits_selected_streams_only(config):
    extractor = components.AgentsStreamCatalogExtractor(config=config)
    records = list(extractor.extract_records(_connection_catalog_response()))

    names = {r["stream_name"] for r in records}
    assert names == {"users", "orders"}
    assert "unselected" not in names


def test_catalog_extractor_derives_table_namespace_columns_and_freshness(config):
    extractor = components.AgentsStreamCatalogExtractor(config=config)
    by_name = {r["stream_name"]: r for r in extractor.extract_records(_connection_catalog_response())}

    users = by_name["users"]
    assert users["destination_namespace"] == "public"
    assert users["destination_table_name"] == "raw_users"
    assert users["primary_key"] == [["id"]]
    assert users["destination_sync_mode"] == "append_dedup"
    assert users["workspace_id"] == "ws-1"

    # freshness surfaced from the connection level
    assert users["last_sync_status"] == "succeeded"
    assert users["last_sync_at"] == 1775182720
    assert users["is_syncing"] is False

    # field selection on: selected_fields + columns restricted to selection, with types
    assert users["selected_fields"] == ["id", "email"]
    assert users["columns"] == [
        {"name": "id", "type": "integer"},
        {"name": "email", "type": ["null", "string"]},
    ]

    # field selection off: all JSON Schema properties become typed columns
    orders = by_name["orders"]
    assert orders["selected_fields"] == []
    assert orders["columns"] == [{"name": "order_id", "type": "integer"}]


@pytest.mark.parametrize(
    "selected_fields, expected",
    [
        pytest.param([{"fieldPath": ["id"]}, {"fieldPath": ["email"]}], ["id", "email"], id="well_formed"),
        pytest.param([{"fieldPath": None}], [], id="null_field_path"),
        pytest.param([{"fieldPath": []}], [], id="empty_field_path"),
        pytest.param([{}], [], id="missing_field_path"),
        pytest.param([{"fieldPath": ["id"]}, {"fieldPath": None}], ["id"], id="mixed_valid_and_null"),
    ],
)
def test_selected_field_names_tolerates_malformed_selected_fields(selected_fields, expected):
    stream_config = {"fieldSelectionEnabled": True, "selectedFields": selected_fields}
    assert components._selected_field_names(stream_config) == expected


def test_root_extractor_emits_index_and_skill(config):
    extractor = components.AgentsRootExtractor(config=config)
    response = Mock()
    response.json.return_value = {"destinationId": DESTINATION_ID}
    records = list(extractor.extract_records(response))

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
