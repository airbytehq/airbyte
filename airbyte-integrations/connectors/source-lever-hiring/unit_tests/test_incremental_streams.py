#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from source_lever_hiring.source import SourceLeverHiring


def get_stream_by_name(stream_name: str, config: Mapping[str, Any]) -> Stream:
    source = SourceLeverHiring()
    matches_by_name = [stream_config for stream_config in source.streams(config) if stream_config.name == stream_name]
    if not matches_by_name:
        raise ValueError("Please provide a valid stream name.")
    return matches_by_name[0]


def test_cursor_field(config_pass):
    stream = get_stream_by_name("opportunities", config_pass)
    expected_cursor_field = "updatedAt"
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(requests_mock, config_pass, opportunities_url, auth_url, auth_token, mock_opportunities_response):
    requests_mock.get(url=opportunities_url, status_code=200, json=mock_opportunities_response)
    requests_mock.post(url=auth_url, json=auth_token)
    stream = get_stream_by_name("opportunities", config_pass)
    stream.state = {"updatedAt": 1600000000000}
    records = []
    for stream_slice in stream.stream_slices(sync_mode=SyncMode.incremental):
        for record in stream.read_records(sync_mode=SyncMode.incremental, stream_slice=stream_slice):
            record_dict = dict(record)
            records.append(record_dict)
            new_stream_state = record_dict.get("updatedAt")
            stream.state = {"updatedAt": new_stream_state}
    expected_state = {"updatedAt": 1738542849132}
    assert stream.state == expected_state


def test_stream_slices(requests_mock, config_pass, opportunities_url, auth_url, auth_token, mock_opportunities_response):
    requests_mock.get(url=opportunities_url, status_code=200, json=mock_opportunities_response)
    requests_mock.post(url=auth_url, json=auth_token)
    stream = get_stream_by_name("opportunities", config_pass)
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": ["updatedAt"], "stream_state": {"updatedAt": 1600000000000}}
    assert stream.stream_slices(**inputs) is not None


def test_supports_incremental(config_pass):
    stream = get_stream_by_name("opportunities", config_pass)
    assert stream.supports_incremental


def test_source_defined_cursor(config_pass):
    stream = get_stream_by_name("opportunities", config_pass)
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(config_pass):
    stream = get_stream_by_name("opportunities", config_pass)
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
