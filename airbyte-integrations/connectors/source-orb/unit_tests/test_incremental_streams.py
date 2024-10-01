#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

import pytest
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from source_orb.source import SourceOrb


def get_stream_by_name(stream_name: str, config: Mapping[str, Any]) -> Stream:
    source = SourceOrb()
    matches_by_name = [stream_config for stream_config in source.streams(config) if stream_config.name == stream_name]
    if not matches_by_name:
        raise ValueError("Please provide a valid stream name.")
    return matches_by_name[0]


def test_cursor_field(config_pass):
    stream = get_stream_by_name("subscriptions", config_pass)
    expected_cursor_field = "created_at"
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(requests_mock, config_pass, subscriptions_url, mock_subscriptions_response):
    requests_mock.get(url=subscriptions_url, status_code=200, json=mock_subscriptions_response)
    stream = get_stream_by_name("subscriptions", config_pass)
    stream.state = {"created_at": "2020-01-10T00:00:00.000Z"}
    records = []
    for stream_slice in stream.stream_slices(sync_mode=SyncMode.incremental):
        for record in stream.read_records(sync_mode=SyncMode.incremental, stream_slice=stream_slice):
            record_dict = dict(record)
            records.append(record_dict)
            new_stream_state = record_dict.get("created_at")
            stream.state = {"created_at": new_stream_state}
    expected_state = {"created_at": "2024-06-21T22:27:22.237Z"}
    assert stream.state == expected_state


def test_stream_slices(requests_mock, config_pass, subscriptions_url, mock_subscriptions_response):
    requests_mock.get(url=subscriptions_url, status_code=200, json=mock_subscriptions_response)
    stream = get_stream_by_name("subscriptions", config_pass)
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": ["created_at"], "stream_state": {"updatedAt": "2020-01-10T00:00:00.000Z"}}
    assert stream.stream_slices(**inputs) is not None


def test_supports_incremental(config_pass):
    stream = get_stream_by_name("subscriptions", config_pass)
    assert stream.supports_incremental


def test_source_defined_cursor(config_pass):
    stream = get_stream_by_name("subscriptions", config_pass)
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(config_pass):
    stream = get_stream_by_name("subscriptions", config_pass)
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
