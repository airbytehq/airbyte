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
from source_hubspot.errors import HubspotInvalidAuth


@pytest.fixture(name="wrong_credentials")
def wrong_credentials_fixture():
    return {"api_key": "wrongkey-key1-key2-key3-wrongkey1234"}


def test__health_check_with_wrong_token(wrong_credentials):
    client = Client(start_date="2021-02-01T00:00:00Z", credentials=wrong_credentials)
    alive, error = client.health_check()

    assert not alive
    assert (
        error
        == "HubspotInvalidAuth('The API key provided is invalid. View or manage your API key here: https://app.hubspot.com/l/api-key/')"
    )


def test__stream_iterator_with_wrong_token(wrong_credentials):
    client = Client(start_date="2021-02-01T00:00:00Z", credentials=wrong_credentials)
    with pytest.raises(
        HubspotInvalidAuth, match="The API key provided is invalid. View or manage your API key here: https://app.hubspot.com/l/api-key/"
    ):
        _ = list(client.streams)
