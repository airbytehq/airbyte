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

import json

import pytest
from source_mailchimp.client import Client


class TestSourceMailchimp:
    mailchimp_config: str = "../secrets/config.json"

    @pytest.fixture()
    def get_client(self):
        with open(self.mailchimp_config) as json_file:
            config = json.load(json_file)
        client = Client(username=config["username"], apikey=config["apikey"])
        return client

    def test_client_right_credentials(self, get_client):
        status, error = get_client.health_check()
        assert status

    def test_client_getting_streams(self, get_client):
        streams = get_client.get_streams()
        assert streams

    def test_client_read_lists(self, get_client):
        lists = list(get_client.lists())
        assert isinstance(lists, list)

    def test_client_read_campaigns(self, get_client):
        campaigns = list(get_client.campaigns())
        assert isinstance(campaigns, list)
