"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import pytest
from source_hubspot.client import Client


@pytest.fixture(name="some_credentials")
def some_credentials_fixture():
    return {"api_key": "wrong_key"}


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
