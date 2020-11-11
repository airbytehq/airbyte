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
from source_mailchimp.client import Client

USERNAME_TEST = "flamingphoenix7"
APIKEY_TEST = "83e165c775226719f9180432221ed508-us2"


def test_client_wrong_credentials():
    with pytest.raises(ValueError, match="The API key that you have entered is not valid"):
        Client(username="unknown_user", apikey="wrong_key")


def test_client_right_credentials():
    client = Client(username=USERNAME_TEST, apikey=APIKEY_TEST)
    status, error = client.health_check()
    assert status


def test_client_getting_streams():
    client = Client(username=USERNAME_TEST, apikey=APIKEY_TEST)
    streams = client.get_streams()
    assert streams


def test_client_read_lists():
    client = Client(username=USERNAME_TEST, apikey=APIKEY_TEST)
    lists = list(client.lists())
    assert isinstance(lists, list)


def test_client_read_campaigns():
    client = Client(username=USERNAME_TEST, apikey=APIKEY_TEST)
    campaigns = list(client.campaigns())
    assert isinstance(campaigns, list)
