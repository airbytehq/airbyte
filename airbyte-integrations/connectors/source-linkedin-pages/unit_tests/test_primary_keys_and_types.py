# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
from typing import Any

import pytest
import requests_mock
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_CONFIG = {
    "org_id": "12345678",
    "credentials": {"auth_method": "access_token", "access_token": "test_token"},
    "start_date": "2023-10-31T00:00:00Z",
    "time_granularity_type": "DAY",
}

_BASE_URL = "https://api.linkedin.com/rest"

_STREAM_PRIMARY_KEYS = [
    pytest.param("organization_lookup", [["id"]], id="organization_lookup"),
    pytest.param("follower_statistics", [["organizationalEntity"]], id="follower_statistics"),
    pytest.param("share_statistics", [["organizationalEntity"]], id="share_statistics"),
    pytest.param("total_follower_count", [["organizationalEntity"]], id="total_follower_count"),
    pytest.param(
        "follower_statistics_time_bound",
        [["organizationalEntity"], ["timeRangeStart"]],
        id="follower_statistics_time_bound",
    ),
    pytest.param(
        "share_statistics_time_bound",
        [["organizationalEntity"], ["timeRangeStart"]],
        id="share_statistics_time_bound",
    ),
]

_TIME_BOUND_STREAMS = [
    pytest.param("follower_statistics_time_bound", "/organizationalEntityFollowerStatistics", id="follower_statistics"),
    pytest.param("share_statistics_time_bound", "/organizationalEntityShareStatistics", id="share_statistics"),
]


def _discovered_streams():
    catalog = get_source(_CONFIG).discover(logging.getLogger(__name__), _CONFIG)
    return {stream.name: stream for stream in catalog.streams}


def _schema_field(schema: dict[str, Any], path: list[str]) -> dict[str, Any]:
    for field in path:
        schema = schema["properties"][field]
    return schema


@pytest.mark.parametrize("stream_name, primary_key", _STREAM_PRIMARY_KEYS)
def test_streams_declare_primary_keys(stream_name: str, primary_key: list[list[str]]) -> None:
    assert _discovered_streams()[stream_name].source_defined_primary_key == primary_key


def test_epoch_millisecond_fields_are_integers_and_date_is_a_date() -> None:
    streams = _discovered_streams()

    for stream_name in ("follower_statistics_time_bound", "share_statistics_time_bound"):
        schema = streams[stream_name].json_schema
        start_type = _schema_field(schema, ["timeRangeStart"])["type"]
        assert "integer" in start_type
        assert "number" not in start_type
        assert _schema_field(schema, ["timeRangeEnd"])["type"] == "integer"
        assert _schema_field(schema, ["date"])["format"] == "date"

    organization_schema = streams["organization_lookup"].json_schema
    for path in (["created", "time"], ["lastModified", "time"], ["id"]):
        field_type = _schema_field(organization_schema, path)["type"]
        assert "integer" in field_type
        assert "number" not in field_type


def test_total_follower_count_includes_organizational_entity() -> None:
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/networkSizes/urn:li:organization:12345678", json={"firstDegreeSize": 10})
        catalog = CatalogBuilder().with_stream("total_follower_count", SyncMode.full_refresh).build()
        output = read(get_source(_CONFIG), config=_CONFIG, catalog=catalog)

    assert output.errors == [], output.get_formatted_error_message()
    records = [message.record.data for message in output.records if message.record.stream == "total_follower_count"]
    assert records[0]["organizationalEntity"] == "urn:li:organization:12345678"


@pytest.mark.parametrize("stream_name, path", _TIME_BOUND_STREAMS)
def test_time_bound_streams_emit_integer_timestamps_and_unique_keys(stream_name: str, path: str) -> None:
    elements = [
        {
            "organizationalEntity": "urn:li:organization:12345678",
            "timeRange": {"start": 1792540800000, "end": 1792627200000},
        },
        {
            "organizationalEntity": "urn:li:organization:12345678",
            "timeRange": {"start": 1792627200000, "end": 1792713600000},
        },
    ]
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}{path}", json={"elements": elements})
        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
        output = read(get_source(_CONFIG), config=_CONFIG, catalog=catalog)

    assert output.errors == [], output.get_formatted_error_message()
    records = [message.record.data for message in output.records if message.record.stream == stream_name]
    assert records[0]["timeRangeStart"] == 1792540800000
    assert records[0]["timeRangeEnd"] == 1792627200000
    assert records[0]["date"] == "2026-10-21"
    keys = [(record["organizationalEntity"], record["timeRangeStart"]) for record in records]
    assert len(keys) == len(set(keys))
