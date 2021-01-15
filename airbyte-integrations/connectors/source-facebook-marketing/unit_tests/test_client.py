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
from airbyte_protocol import AirbyteStream
from source_facebook_marketing.client import Client, FacebookAPIException


def test__health_check_with_wrong_token():
    client = Client(account_id="wrong_account", access_token="wrong_key", start_date="2019-03-03T10:00")
    alive, error = client.health_check()

    assert not alive
    assert error == "Error: 190, Invalid OAuth access token."


def test__campaigns_with_wrong_token():
    client = Client(account_id="wrong_account", access_token="wrong_key", start_date="2019-03-03T10:00")
    with pytest.raises(FacebookAPIException, match="Error: 190, Invalid OAuth access token"):
        next(client.read_stream(AirbyteStream(name="campaigns", json_schema={})))
