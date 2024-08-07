#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

from airbyte_cdk.sources.streams import Stream
from airbyte_protocol.models import SyncMode
from jsonref import requests
from source_lever_hiring.source import SourceLeverHiring


def get_stream_by_name(stream_name: str, config: Mapping[str, Any]) -> Stream:
    source = SourceLeverHiring()
    matches_by_name = [stream_config for stream_config in source.streams(config) if stream_config.name == stream_name]
    if not matches_by_name:
        raise ValueError("Please provide a valid stream name.")
    return matches_by_name[0]


def test_request_params(config_pass):
    stream = get_stream_by_name("users", config_pass)
    expected_params = {"includeDeactivated": "True"}
    assert stream.retriever.requester.get_request_params() == expected_params


def test_next_page_token(requests_mock, config_pass, users_url, auth_url, auth_token, mock_users_response):
    requests_mock.get(url=users_url, status_code=200, json=mock_users_response)
    requests_mock.post(url=auth_url, json=auth_token)
    stream = get_stream_by_name("users", config_pass)
    inputs = {"response": requests.get(users_url)}
    expected_token = {"next_page_token": "%5B1628543173558%2C%227bf8c1ac-4a68-450f-bea0-a1e2c3f5aeaf%22%5D"}
    assert stream.retriever._next_page_token(**inputs) == expected_token


def test_parse_response(requests_mock, config_pass, users_url, auth_url, auth_token, mock_users_response_no_next):
    requests_mock.get(url=users_url, status_code=200, json=mock_users_response_no_next)
    requests_mock.post(url=auth_url, json=auth_token)
    stream = get_stream_by_name("users", config_pass)
    expected_parsed_records = [{
        "id": "fake_id",
        "name": "fake_name",
        "contact": "fake_contact",
        "headline": "Airbyte",
        "stage": "offer",
        "confidentiality": "non-confidential",
        "location": "Los Angeles, CA",
        "origin": "referred",
        "createdAt": 1628510997134,
        "updatedAt": 1628542848755,
        "isAnonymized": False,
    }]
    records = []
    for stream_slice in stream.stream_slices(sync_mode=SyncMode.full_refresh):
        records.extend(list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)))
    records.sort()
    expected_parsed_records.sort()
    assert len(records) == len(expected_parsed_records)
    for i in range(len(records)):
        assert sorted(records[i].keys()) == sorted(expected_parsed_records[i].keys())


def test_request_headers(requests_mock, config_pass, users_url, auth_url, auth_token, mock_users_response):
    requests_mock.get(url=users_url, status_code=200, json=mock_users_response)
    requests_mock.post(url=auth_url, json=auth_token)
    stream = get_stream_by_name("users", config_pass)
    inputs = {
        "stream_slice": {"slice": "test_slice"},
        "stream_state": {"updatedAt": 1600000000000},
        "next_page_token": {"offset": "next_page_cursor"},
    }
    assert stream.retriever.requester.get_request_headers(**inputs) == {}


def test_http_method(requests_mock, config_pass, users_url, auth_url, auth_token, mock_users_response):
    requests_mock.get(url=users_url, status_code=200, json=mock_users_response)
    requests_mock.post(url=auth_url, json=auth_token)
    stream = get_stream_by_name("users", config_pass)
    expected_method = "GET"
    assert stream.retriever.requester.http_method.value == expected_method


def test_should_retry(requests_mock, config_pass, users_url, auth_url, auth_token):
    requests_mock.get(url=users_url, status_code=200)
    requests_mock.post(auth_url, json=auth_token)
    stream = get_stream_by_name("users", config_pass)
    records = []
    for stream_slice in stream.stream_slices(sync_mode=SyncMode.full_refresh):
        records.extend(list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)))
    assert records == []
    assert requests_mock.call_count == 2
