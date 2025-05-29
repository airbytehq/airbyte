#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

import pytest
from airbyte_cdk.sources.streams import Stream
from airbyte_protocol.models import SyncMode
from jsonref import requests
from source_salesloft.source import SourceSalesloft


def mock_response():
    return {"data": [{"id": "mock1"}, {"id": "mock2"}]}


def get_stream_by_name(stream_name: str, config: Mapping[str, Any]) -> Stream:
    source = SourceSalesloft()
    matches_by_name = [stream_config for stream_config in source.streams(config) if stream_config.name == stream_name]
    if not matches_by_name:
        raise ValueError("Please provide a valid stream name.")
    return matches_by_name[0]


def test_request_params(config):
    stream = get_stream_by_name("users", config)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {}
    assert stream.retriever.requester.get_request_params(**inputs) == expected_params


def test_incremental_request_params(config):
    stream = get_stream_by_name("accounts", config)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {
        "created_at[gt]": "2020-01-01T00:00:00.000Z",
        "updated_at[gt]": "2020-01-01T00:00:00.000000Z",
    }
    assert stream.retriever.requester.get_request_params(**inputs) == expected_params


def test_next_page_token(requests_mock, config):
    stream = get_stream_by_name("users", config)
    response = {"metadata": {"paging": {"next_page": 2}}}
    requests_mock.post("https://accounts.salesloft.com/oauth/token", json={"access_token": "token", "expires_in": 7200})
    requests_mock.get("https://api.salesloft.com/v2/users", status_code=200, json=response)
    inputs = {"response": requests.get("https://api.salesloft.com/v2/users")}
    expected_token = {"next_page_token": 2}
    assert stream.retriever._next_page_token(**inputs) == expected_token


def test_next_page_token_invalid(requests_mock, config):
    stream = get_stream_by_name("users", config)
    response = {"metadata": {"paginfffg": {"next_pagaae": 2}}}
    requests_mock.post("https://accounts.salesloft.com/oauth/token", json={"access_token": "token", "expires_in": 7200})
    requests_mock.get("https://api.salesloft.com/v2/users", status_code=200, json=response)
    inputs = {"response": requests.get("https://api.salesloft.com/v2/users")}
    with pytest.raises(AttributeError) as ex:
        stream.retriever._next_page_token(**inputs).get("next_page_token")
    assert isinstance(ex.value, AttributeError)


def test_get_updated_state(config):
    stream = get_stream_by_name("accounts", config)
    inputs = {"current_stream_state": {}, "latest_record": {}}
    expected_state = {}
    assert stream.get_updated_state(**inputs) == expected_state


@pytest.mark.parametrize(
    "return_value, expected_records", (({"metadata": {}}, []), ({"data": [{"id": 1}, {"id": 2}], "metadata": {}}, [{"id": 1}, {"id": 2}]))
)
def test_parse_response(requests_mock, config, return_value, expected_records):
    stream = get_stream_by_name("users", config)
    requests_mock.post("https://accounts.salesloft.com/oauth/token", json={"access_token": "token", "expires_in": 7200})
    requests_mock.get("https://api.salesloft.com/v2/users", status_code=200, json=return_value)
    records = []
    for stream_slice in stream.stream_slices(sync_mode=SyncMode.full_refresh):
        records.extend(list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)))
    assert len(records) == len(expected_records)
    for i in range(len(records)):
        assert records[i].keys() == expected_records[i].keys()


def test_stream_has_path(config):
    for stream in SourceSalesloft().streams(config):
        assert stream.retriever.requester.path
