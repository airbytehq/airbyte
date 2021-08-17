#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


import pytest
from source_hubspot.api import API
from source_hubspot.client import Client


@pytest.fixture(name="some_credentials")
def some_credentials_fixture():
    return {"api_key": "wrong_key"}


@pytest.fixture(name="creds_with_wrong_permissions")
def creds_with_wrong_permissions():
    return {"api_key": "THIS-IS-THE-API_KEY"}


def test_client_backoff_on_limit_reached(requests_mock, some_credentials):
    """Error once, check that we retry and not fail"""
    responses = [
        {"json": {"error": "limit reached"}, "status_code": 429, "headers": {"Retry-After": "0"}},
        {"json": [], "status_code": 200},
    ]

    requests_mock.register_uri("GET", "/properties/v2/contact/properties", responses)
    client = Client(start_date="2021-02-01T00:00:00Z", credentials=some_credentials)

    alive, error = client.health_check()

    assert alive
    assert not error


def test_client_backoff_on_server_error(requests_mock, some_credentials):
    """Error once, check that we retry and not fail"""
    responses = [
        {"json": {"error": "something bad"}, "status_code": 500},
        {"json": [], "status_code": 200},
    ]
    requests_mock.register_uri("GET", "/properties/v2/contact/properties", responses)
    client = Client(start_date="2021-02-01T00:00:00Z", credentials=some_credentials)

    alive, error = client.health_check()

    assert alive
    assert not error


def test_wrong_permissions_api_key(requests_mock, creds_with_wrong_permissions):
    """
    Error with API Key Permissions to particular stream,
    typically this issue raises along with calling `workflows` stream with API Key
    that doesn't have required permissions to read the stream.
    """
    # Define stream name
    stream_name = "workflows"

    # Mapping tipical response for mocker
    responses = [
        {
            "json": {
                "status": "error",
                "message": f'This hapikey ({creds_with_wrong_permissions.get("api_key")}) does not have proper permissions! (requires any of [automation-access])',
                "correlationId": "2fe0a9af-3609-45c9-a4d7-83a1774121aa",
            }
        }
    ]

    # We expect something like this
    expected_warining_message = {
        "type": "LOG",
        "log": {
            "level": "WARN",
            "message": f'Stream `workflows` cannot be procced. This hapikey ({creds_with_wrong_permissions.get("api_key")}) does not have proper permissions! (requires any of [automation-access])',
        },
    }

    # create base parent instances
    client = Client(start_date="2021-02-01T00:00:00Z", credentials=creds_with_wrong_permissions)
    api = API(creds_with_wrong_permissions)

    # Create test_stream instance
    test_stream = client._apis.get(stream_name)

    # Mocking Request
    requests_mock.register_uri("GET", test_stream.url, responses)

    # Mock the getter method that handles requests.
    def get(url=test_stream.url, params=None):
        response = api._session.get(api.BASE_URL + url, params=api._add_auth(params))
        return api._parse_and_handle_errors(response)

    # Define request params value
    params = {"limit": 100, "properties": ""}

    # Read preudo-output from generator object _read(), based on real scenario
    list(test_stream._read(getter=get, params=params))

    # match logged expected logged warning message with output given from preudo-output
    assert expected_warining_message
