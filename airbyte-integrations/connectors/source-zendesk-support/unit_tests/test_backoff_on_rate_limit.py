#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any, Dict, Mapping

import requests
from source_zendesk_support.source import SourceZendeskSupport
from source_zendesk_support.streams import Users


def read_config(config_path: str) -> Mapping[str, Any]:
    """
    Get the config from /test_input
    """
    with open(config_path, "r") as f:
        return json.loads(f.read())


def prepare_config(config: Dict):
    return SourceZendeskSupport().convert_config2stream_args(config)


# create client
config = prepare_config(read_config("secrets/config.json"))
# test stream
TEST_STREAM = Users(**config)


def test_backoff(requests_mock):
    """ """
    test_response_header = {"Retry-After": "5", "X-Rate-Limit": "0"}
    test_response_json = {"count": {"value": 1, "refreshed_at": "2022-03-29T10:10:51+00:00"}}
    expected = int(test_response_header.get("Retry-After"))

    url = f"{TEST_STREAM.url_base}{TEST_STREAM.path()}/count.json"
    requests_mock.get(url, json=test_response_json, headers=test_response_header, status_code=429)
    test_response = requests.get(url)

    actual = TEST_STREAM.backoff_time(test_response)
    assert actual == expected
