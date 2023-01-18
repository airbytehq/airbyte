#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import copy
import logging
from unittest.mock import patch

from airbyte_cdk.models.airbyte_protocol import SyncMode
from airbyte_cdk.sources.singer import SingerHelper, SyncModeInfo
from airbyte_cdk.sources.singer.source import BaseSingerSource, ConfigContainer

logger = logging.getLogger("airbyte")


class TetsBaseSinger(BaseSingerSource):
    tap_cmd = ""


USER_STREAM = {
    "type": "SCHEMA",
    "stream": "users",
    "schema": {
        "properties": {"id": {"type": "integer"}, "name": {"type": "string"}, "updated_at": {"type": "string", "format": "date-time"}}
    },
    "key_properties": ["id"],
    "bookmark_properties": ["updated_at"],
}

ROLES_STREAM = {
    "type": "SCHEMA",
    "stream": "roles",
    "schema": {
        "properties": {
            "name": {"type": "string"},
        }
    },
    "key_properties": ["name"],
    "bookmark_properties": ["updated_at"],
    "metadata": [
        {
            "metadata": {
                "inclusion": "available",
                "table-key-properties": ["id"],
                "selected": True,
                "valid-replication-keys": ["name"],
                "schema-name": "roles",
            },
            "breadcrumb": [],
        }
    ],
}

basic_singer_catalog = {"streams": [USER_STREAM, ROLES_STREAM]}


@patch.object(SingerHelper, "_read_singer_catalog", return_value=basic_singer_catalog)
def test_singer_discover_single_pk(mock_read_catalog):
    airbyte_catalog = TetsBaseSinger().discover(logger, ConfigContainer({}, ""))
    _user_stream = airbyte_catalog.streams[0]
    _roles_stream = airbyte_catalog.streams[1]
    assert _user_stream.source_defined_primary_key == [["id"]]
    assert _roles_stream.json_schema == ROLES_STREAM["schema"]
    assert _user_stream.json_schema == USER_STREAM["schema"]


def test_singer_discover_with_composite_pk():
    singer_catalog_composite_pk = copy.deepcopy(basic_singer_catalog)
    singer_catalog_composite_pk["streams"][0]["key_properties"] = ["id", "name"]
    with patch.object(SingerHelper, "_read_singer_catalog", return_value=singer_catalog_composite_pk):
        airbyte_catalog = TetsBaseSinger().discover(logger, ConfigContainer({}, ""))

    _user_stream = airbyte_catalog.streams[0]
    _roles_stream = airbyte_catalog.streams[1]
    assert _user_stream.source_defined_primary_key == [["id"], ["name"]]
    assert _roles_stream.json_schema == ROLES_STREAM["schema"]
    assert _user_stream.json_schema == USER_STREAM["schema"]


@patch.object(BaseSingerSource, "get_primary_key_overrides", return_value={"users": ["updated_at"]})
@patch.object(SingerHelper, "_read_singer_catalog", return_value=basic_singer_catalog)
def test_singer_discover_pk_overrides(mock_pk_override, mock_read_catalog):
    airbyte_catalog = TetsBaseSinger().discover(logger, ConfigContainer({}, ""))
    _user_stream = airbyte_catalog.streams[0]
    _roles_stream = airbyte_catalog.streams[1]
    assert _user_stream.source_defined_primary_key == [["updated_at"]]
    assert _roles_stream.json_schema == ROLES_STREAM["schema"]
    assert _user_stream.json_schema == USER_STREAM["schema"]


@patch.object(SingerHelper, "_read_singer_catalog", return_value=basic_singer_catalog)
def test_singer_discover_metadata(mock_read_catalog):
    airbyte_catalog = TetsBaseSinger().discover(logger, ConfigContainer({}, ""))
    _user_stream = airbyte_catalog.streams[0]
    _roles_stream = airbyte_catalog.streams[1]

    # assert _user_stream.supported_sync_modes is None
    assert _user_stream.default_cursor_field is None
    assert _roles_stream.supported_sync_modes == [SyncMode.incremental]
    assert _roles_stream.default_cursor_field == ["name"]


@patch.object(SingerHelper, "_read_singer_catalog", return_value=basic_singer_catalog)
def test_singer_discover_sync_mode_overrides(mock_read_catalog):
    sync_mode_override = SyncModeInfo(supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental], default_cursor_field=["name"])
    with patch.object(BaseSingerSource, "get_sync_mode_overrides", return_value={"roles": sync_mode_override}):
        airbyte_catalog = TetsBaseSinger().discover(logger, ConfigContainer({}, ""))

    _roles_stream = airbyte_catalog.streams[1]
    assert _roles_stream.supported_sync_modes == sync_mode_override.supported_sync_modes
    assert _roles_stream.default_cursor_field == sync_mode_override.default_cursor_field
