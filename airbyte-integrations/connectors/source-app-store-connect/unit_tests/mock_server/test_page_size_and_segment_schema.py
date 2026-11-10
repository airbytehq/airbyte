# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import jsonschema
import pytest

from airbyte_cdk.test.entrypoint_wrapper import discover
from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.conftest import get_source

from .analytics_helpers import DOWNLOAD_URL, SEGMENT_ID, expected_record_id, read_analytics_stream
from .config import ConfigBuilder
from .request_builder import RequestBuilder
from .response_builder import fixture_response
from .utils import read_output


_SEGMENT_STREAMS = [
    "analytics_installations_segments",
    "analytics_installations_segments_historical",
    "analytics_app_download_segments",
    "analytics_app_download_segments_historical",
]


def test_list_id_apps_requests_max_page_size_on_every_page() -> None:
    with HttpMocker() as http_mocker:
        first_page = RequestBuilder.apps_endpoint().build()
        http_mocker.get(
            first_page,
            fixture_response("list_id_apps", next_url=f"{RequestBuilder.apps_endpoint().url}?cursor=PAGE_TWO&limit=200"),
        )
        http_mocker.get(
            RequestBuilder.apps_endpoint().with_cursor("PAGE_TWO").build(),
            fixture_response("list_id_apps", id_suffix="-page-2"),
        )

        output = read_output(ConfigBuilder(), "list_id_apps")

    assert [record.record.data["id"] for record in output.records] == ["app-1", "app-1-page-2"]


@pytest.mark.parametrize(
    "stream_name",
    [
        "analytics_report_requests_ongoing",
        "analytics_installations_reports",
        "analytics_installations_instances",
        "analytics_installations_segments",
    ],
)
def test_analytics_collections_request_max_page_size_on_every_page(stream_name: str) -> None:
    with HttpMocker() as http_mocker:
        output = read_analytics_stream(http_mocker, stream_name, paginate=True)

    expected_id = expected_record_id(stream_name)
    assert [record.record.data["id"] for record in output.records] == [expected_id, f"{expected_id}-page-2"]


@pytest.mark.parametrize("stream_name", _SEGMENT_STREAMS)
def test_segment_records_conform_to_discovered_schema(stream_name: str) -> None:
    with HttpMocker() as http_mocker:
        output = read_analytics_stream(http_mocker, stream_name)
    config = ConfigBuilder().build()
    catalog = discover(get_source(config), config).catalog.catalog
    schema = next(stream.json_schema for stream in catalog.streams if stream.name == stream_name)

    assert len(output.records) == 1
    record = output.records[0].record.data
    assert record["id"] == SEGMENT_ID
    assert record["attributes"] == {"checksum": "abc123", "sizeInBytes": 42, "url": DOWNLOAD_URL}
    assert set(record) <= set(schema["properties"])
    assert set(record["attributes"]) <= set(schema["properties"]["attributes"]["properties"])
    jsonschema.validate(record, schema)
