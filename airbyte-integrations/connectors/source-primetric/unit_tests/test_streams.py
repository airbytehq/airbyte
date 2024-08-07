#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from source_primetric.source import SourcePrimetric


def get_stream_by_name(stream_name: str, config: Mapping[str, Any]) -> Stream:
    source = SourcePrimetric()
    matches_by_name = [stream_config for stream_config in source.streams(config) if stream_config.name == stream_name]
    if not matches_by_name:
        raise ValueError("Please provide a valid stream name.")
    return matches_by_name[0]


def test_availability_strategy(config_pass):
    assignments = get_stream_by_name("assignments", config_pass)
    assert not assignments.availability_strategy


def test_request_params(config_pass):
    assignments = get_stream_by_name("assignments", config_pass)
    expected_params = {}
    assert assignments.retriever.requester.get_request_params() == expected_params


def test_request_headers(config_pass):
    assignments = get_stream_by_name("assignments", config_pass)
    expected_headers = {}
    assert assignments.retriever.requester.get_request_headers() == expected_headers 


def test_http_method(config_pass):
    assignments = get_stream_by_name("assignments", config_pass)
    expected_method = "GET"
    actual_method = assignments.retriever.requester.http_method.value
    assert actual_method == expected_method


def test_should_retry(requests_mock, assignments_url, config_pass, auth_url, auth_token):
    requests_mock.get(url=assignments_url, status_code=200)
    requests_mock.post(auth_url, json=auth_token)
    stream = get_stream_by_name("assignments", config_pass)

    records = []
    for stream_slice in stream.stream_slices(sync_mode=SyncMode.full_refresh):
        records.extend(list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)))
    assert records == []
    assert requests_mock.call_count == 2 
