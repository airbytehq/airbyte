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
from grnhse.exceptions import EndpointNotFound, HTTPError
from source_greenhouse.client import Client


def test__heal_check_with_wrong_api_key():
    client = Client(api_key="wrong_key")
    alive, error = client.health_check()

    assert not alive
    assert error == '401 {"message":"Invalid Basic Auth credentials"}'


def test__custom_fields_with_wrong_api_key():
    client = Client(api_key="wrong_key")
    with pytest.raises(HTTPError, match='401 {"message":"Invalid Basic Auth credentials"}'):
        list(client.list("custom_fields"))


def test_client_wrong_endpoint():
    client = Client(api_key="wrong_key")
    with pytest.raises(EndpointNotFound, match="unknown_endpoint"):
        next(client.list("unknown_endpoint"))
