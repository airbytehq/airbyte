#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

from source_adjust.source import SourceAdjust

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream


def get_stream_by_name(stream_name: str, config: Mapping[str, Any]) -> Stream:
    source = SourceAdjust(config=config, catalog=None, state=None)
    matches_by_name = [stream_config for stream_config in source.streams(config) if stream_config.name == stream_name]
    if not matches_by_name:
        raise ValueError("Please provide a valid stream name.")
    return matches_by_name[0]


def test_cursor_field(requests_mock, config_pass, report_url, mock_report_response):
    requests_mock.get(url=report_url, status_code=200, json=mock_report_response)
    stream = get_stream_by_name("AdjustReport", config_pass)
    expected_cursor_field = "day"
    assert stream.cursor_field == expected_cursor_field


def test_stream_slices(config_pass):
    stream = get_stream_by_name("AdjustReport", config_pass)
    assert list(stream.cursor.stream_slices())


def test_supports_incremental(config_pass):
    stream = get_stream_by_name("AdjustReport", config_pass)
    assert SyncMode.incremental in stream.as_airbyte_stream().supported_sync_modes


def test_source_defined_cursor(config_pass):
    stream = get_stream_by_name("AdjustReport", config_pass)
    assert stream.as_airbyte_stream().source_defined_cursor
