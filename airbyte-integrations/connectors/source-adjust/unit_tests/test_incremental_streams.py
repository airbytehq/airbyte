#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timedelta
from typing import Any, Mapping

from airbyte_cdk.sources.streams import Stream
from airbyte_protocol.models import SyncMode
from source_adjust.source import SourceAdjust


def get_stream_by_name(stream_name: str, config: Mapping[str, Any]) -> Stream:
    source = SourceAdjust()
    matches_by_name = [stream_config for stream_config in source.streams(config) if stream_config.name == stream_name]
    if not matches_by_name:
        raise ValueError("Please provide a valid stream name.")
    return matches_by_name[0]


def test_cursor_field(requests_mock, config_pass, report_url, mock_report_response):
    requests_mock.get(url=report_url, status_code=200, json=mock_report_response)
    stream = get_stream_by_name("AdjustReport", config_pass)
    expected_cursor_field = "day"
    assert stream.cursor_field == expected_cursor_field


def test_stream_slices(requests_mock, config_pass, report_url, mock_report_response):
    requests_mock.get(url=report_url, status_code=200, json=mock_report_response)
    stream = get_stream_by_name("AdjustReport", config_pass)
    period = 5
    start = datetime.today() - timedelta(days=period)
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": "day", "stream_state": {"day": start.isoformat()}}
    assert list(stream.stream_slices(**inputs)) is not None


def test_supports_incremental(config_pass):
    stream = get_stream_by_name("AdjustReport", config_pass)
    assert stream.supports_incremental


def test_source_defined_cursor(config_pass):
    stream = get_stream_by_name("AdjustReport", config_pass)
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(config_pass):
    stream = get_stream_by_name("AdjustReport", config_pass)
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
