#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
import requests
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder, JsonlDecoder


@pytest.mark.parametrize(
    "response_body, expected_json",
    [
        ("", [{}]),
        ('{"healthcheck": {"status": "ok"}}', [{"healthcheck": {"status": "ok"}}])
    ],

)
def test_json_decoder(requests_mock, response_body, expected_json):
    requests_mock.register_uri("GET", "https://airbyte.io/", text=response_body)
    response = requests.get("https://airbyte.io/")
    assert list(JsonDecoder(parameters={}).decode(response)) == expected_json


@pytest.mark.parametrize(
    "response_body, expected_json",
    [
        ("", []),
        ('{"id": 1, "name": "test1"}', [{"id": 1, "name": "test1"}]),
        ('{"id": 1, "name": "test1"}\n{"id": 2, "name": "test2"}', [{"id": 1, "name": "test1"}, {"id": 2, "name": "test2"}])
    ],
    ids=["empty_response", "one_line_json", "multi_line_json"]
)
def test_jsonl_decoder(requests_mock, response_body, expected_json):
    requests_mock.register_uri("GET", "https://airbyte.io/", text=response_body)
    response = requests.get("https://airbyte.io/")
    assert list(JsonlDecoder(parameters={}).decode(response)) == expected_json
