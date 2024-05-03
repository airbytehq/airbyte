#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
import requests
from airbyte_cdk.sources.streams.http.decoders.json_decoder import JsonDecoder

def test_json_decoder_with_valid_repsonse():
    response = requests.Response()
    response._content = b'{ "test": "all good" }'
    response.status_code = 200
    assert JsonDecoder().decode(response) == { "test": "all good" }

def test_json_decoder_with_invalid_json():
    response = requests.Response()
    decoded_response = JsonDecoder().decode(response)
    assert decoded_response == {}

def test_validate_response_with_valid_response():
    response = requests.Response()
    response._content = b'{"test": "all good" }'
    response.status_code = 200
    assert JsonDecoder().validate_response(response) is None

def test_validate_response_with_4xx_status_code():
    response = requests.Response()
    response.status_code = 400
    assert JsonDecoder().validate_response(response) is None

def test_validate_repsonse_with_ok_response_but_no_json_body():
    response = requests.Response()
    response.status_code = 200
    with pytest.raises(requests.exceptions.JSONDecodeError):
        JsonDecoder().validate_response(response)
