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

import json

import pendulum
import pytest
from airbyte_cdk.models import AirbyteStream
from facebook_business import FacebookSession
from source_facebook_marketing.client import Client


@pytest.fixture(scope="session", name="some_config")
def some_config_fixture():
    return {"start_date": "2021-01-23T00:00:00Z", "account_id": "unknown_account", "access_token": "unknown_token"}


@pytest.fixture(autouse=True)
def mock_default_sleep_interval(mocker):
    mocker.patch("source_facebook_marketing.client.common.DEFAULT_SLEEP_INTERVAL", return_value=pendulum.Interval(seconds=5))


@pytest.fixture(name="client")
def client_fixture(some_config):
    client = Client(**some_config)
    return client


@pytest.fixture(name="fb_call_rate_response")
def fb_call_rate_response_fixture():
    error = {"message": "(#32) Page request limit reached", "type": "OAuthException", "code": 32, "fbtrace_id": "Fz54k3GZrio"}

    headers = {"x-app-usage": json.dumps({"call_count": 28, "total_time": 25, "total_cputime": 25})}

    return {
        "json": {
            "error": error,
        },
        "status_code": 400,
        "headers": headers,
    }


@pytest.fixture(name="fb_account_response")
def fb_account_response_fixture():
    return {
        "json": {
            "data": [
                {
                    "account_id": "unknown_account",
                    "id": "act_unknown_account"
                }
            ],
            "paging": {
                "cursors": {
                    "before": "MjM4NDYzMDYyMTcyNTAwNzEZD",
                    "after": "MjM4NDYzMDYyMTcyNTAwNzEZD"
                }
            }
        },
        "status_code": 200,
    }


class TestBackoff:
    def test_limit_reached(self, requests_mock, client, fb_call_rate_response, fb_account_response):
        """Error once, check that we retry and not fail"""
        campaign_responses = [
            fb_call_rate_response,
            {"json": {"data": [{"id": 1, "updated_time": "2020-09-25T00:00:00Z"}, {"id": 2, "updated_time": "2020-09-25T00:00:00Z"}]}, "status_code": 200},
        ]

        requests_mock.register_uri("GET", FacebookSession.GRAPH + "/v10.0/me/adaccounts", [fb_account_response])
        requests_mock.register_uri("GET", FacebookSession.GRAPH + "/v10.0/act_unknown_account/campaigns", campaign_responses)
        requests_mock.register_uri("GET", FacebookSession.GRAPH + "/v10.0/1/", [{"status_code": 200}])
        requests_mock.register_uri("GET", FacebookSession.GRAPH + "/v10.0/2/", [{"status_code": 200}])

        records = list(client.read_stream(AirbyteStream(name="campaigns", json_schema={})))

        assert records

    def test_batch_limit_reached(self, requests_mock, client, fb_call_rate_response):
        """Error once, check that we retry and not fail"""
        responses = [
            fb_call_rate_response,
            {"json": {"data": [1, 2]}, "status_code": 200},
        ]

        requests_mock.register_uri("GET", FacebookSession.GRAPH, responses)

        records = list(client.read_stream(AirbyteStream(name="adcreatives", json_schema={})))

        assert not records

    def test_server_error(self, requests_mock, client, fb_account_response):
        """Error once, check that we retry and not fail"""
        responses = [
            {"json": {"error": "something bad"}, "status_code": 500},
            {"json": [], "status_code": 200},
        ]

        requests_mock.register_uri("GET", FacebookSession.GRAPH + "/v10.0/me/adaccounts", [fb_account_response])
        requests_mock.register_uri("GET", FacebookSession.GRAPH + "/v10.0/act_unknown_account/campaigns", responses)

        list(client.read_stream(AirbyteStream(name="campaigns", json_schema={})))
