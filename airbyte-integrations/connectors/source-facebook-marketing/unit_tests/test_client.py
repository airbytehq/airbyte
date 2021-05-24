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
# from airbyte_protocol import AirbyteStream
from facebook_business import FacebookSession
from source_facebook_marketing.client import Client


@pytest.fixture(name="some_config")
def some_config_fixture():
    return {
        "start_date": "2021-01-23T00:00:00Z",
        "account_id": "unknown_account",
        "access_token": "unknown_token"
    }


@pytest.fixture(name="client")
def client_fixture(some_config):
    return Client(**some_config)


import logging

# Debug logging
# httplib.HTTPConnection.debuglevel = 1
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
req_log = logging.getLogger('requests.packages.urllib3')
req_log.setLevel(logging.DEBUG)
req_log.propagate = True


@pytest.fixture(name=fb_call_rate_response)
def fb_call_rate_response_fixture():
    error = {
        "message": "(#32) Page request limit reached",
        "type": "OAuthException",
        "code": 32,
        "fbtrace_id": "Fz54k3GZrio"
    }

    headers = {
        "x-app-usage": {
            "call_count": 28,
            "total_time": 25,
            "total_cputime": 25
        }
    }

    return {
        "json": {
            "error": error,
        },
        "status_code": 429, "headers": headers
    }


class TestBackoff:
    def test_limit_reached(self, requests_mock, client, fb_call_rate_response):
        """Error once, check that we retry and not fail"""
        responses = [
            fb_call_rate_response,
            {"json": [], "status_code": 200},
        ]

        url = "https://graph.facebook.com/v10.0/me/adaccounts"
        requests_mock.register_uri("GET", url, responses)

        # AirbyteStream(name="", json_schema={})
        alive, error = client.health_check()

        assert alive
        assert not error

    def test_batch_limit_reached(self, request_mock, client):
        pass

    def test_server_error(self, requests_mock, client):
        """Error once, check that we retry and not fail"""
        responses = [
            {"json": {"error": "something bad"}, "status_code": 500},
            {"json": [], "status_code": 200},
        ]
        requests_mock.register_uri("GET", FacebookSession.GRAPH, responses)

        alive, error = client.health_check()

        assert alive
        assert not error
