#
# Copyright (c) 2024s Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

import pytest
from airbyte_cdk.sources.streams import Stream
from airbyte_protocol.models import SyncMode
from jsonref import requests
from source_orb.source import SourceOrb


def get_stream_by_name(stream_name: str, config: Mapping[str, Any]) -> Stream:
    source = SourceOrb()
    matches_by_name = [stream_config for stream_config in source.streams(config) if stream_config.name == stream_name]
    if not matches_by_name:
        raise ValueError("Please provide a valid stream name.")
    return matches_by_name[0]


def test_request_params(config_pass):
    stream = get_stream_by_name("subscriptions", config_pass)
    expected_params = {}
    assert stream.retriever.requester.get_request_params() == expected_params


@pytest.mark.parametrize(
    ("mock_response", "expected_token"),
    [
        ({}, None),
        (dict(pagination_metadata=dict(has_more=True, next_cursor="orb-test-cursor")), dict(next_page_token="orb-test-cursor")),
        (dict(pagination_metadata=dict(has_more=False)), None),
    ],
)
def test_next_page_token(requests_mock, config_pass, subscriptions_url, mock_response, expected_token):
    requests_mock.get(url=subscriptions_url, status_code=200, json=mock_response)
    stream = get_stream_by_name("subscriptions", config_pass)
    inputs = {"response": requests.get(subscriptions_url)}
    assert stream.retriever._next_page_token(**inputs) == expected_token


@pytest.mark.parametrize(
    ("mock_response", "expected_parsed_records"),
    [
        ({}, []),
        (dict(data=[]), []),
        (dict(data=[{"id": "test-customer-id", "customer": {"id": "1", "external_customer_id": "2"}, "plan": {"id": "3"}}]),
         [{"id": "test-customer-id", "customer_id": "1", "external_customer_id": "2", "plan_id": "3"}]),
        (dict(data=[{"id": "test-customer-id", "customer": {"id": "7", "external_customer_id": "8"}, "plan": {"id": "9"}},
                    {"id": "test-customer-id-2", "customer": {"id": "10", "external_customer_id": "11"}, "plan": {"id": "12"}}]),
         [{"id": "test-customer-id", "customer_id": "7", "external_customer_id": "8", "plan_id": "9"},
          {"id": "test-customer-id-2", "customer_id": "10", "external_customer_id": "11", "plan_id": "9"}]),
    ],
)
def test_parse_response(requests_mock, config_pass, subscriptions_url, mock_response, expected_parsed_records):
    requests_mock.get(url=subscriptions_url, status_code=200, json=mock_response)
    stream = get_stream_by_name("subscriptions", config_pass)
    records = []
    for stream_slice in stream.stream_slices(sync_mode=SyncMode.full_refresh):
        records.extend(list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)))
    assert len(records) == len(expected_parsed_records)
    for i in range(len(records)):
        assert sorted(records[i].keys()) == sorted(expected_parsed_records[i].keys())


def test_http_method(config_pass):
    stream = get_stream_by_name("subscriptions", config_pass)
    expected_method = "GET"
    assert stream.retriever.requester.http_method.value == expected_method


def test_subscription_usage_schema(config_pass):
    stream = get_stream_by_name("subscription_usage", config_pass)
    json_schema = stream.get_json_schema()
    assert len(json_schema["properties"]) == 7
