#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
import requests
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder


@pytest.mark.parametrize(
    "response_body, expected_json", (("", {}), ('{"healthcheck": {"status": "ok"}}', {"healthcheck": {"status": "ok"}}))
)
def test_json_decoder(requests_mock, response_body, expected_json):
    requests_mock.register_uri("GET", "https://airbyte.io/", text=response_body)
    response = requests.get("https://airbyte.io/")
    assert JsonDecoder(options={}).decode(response) == expected_json
