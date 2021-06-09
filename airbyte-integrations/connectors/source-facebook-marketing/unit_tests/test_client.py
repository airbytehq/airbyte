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
from facebook_business.exceptions import FacebookRequestError
from source_facebook_marketing.client import Client


@pytest.fixture(scope="session", name="account_id")
def account_id_fixture():
    return "unknown_account"


@pytest.fixture(scope="session", name="some_config")
def some_config_fixture(account_id):
    return {"start_date": "2021-01-23T00:00:00Z", "account_id": f"{account_id}", "access_token": "unknown_token"}


@pytest.fixture(autouse=True)
def mock_default_sleep_interval(mocker):
    mocker.patch("source_facebook_marketing.client.common.DEFAULT_SLEEP_INTERVAL", return_value=pendulum.Interval(seconds=5))


@pytest.fixture(name="client")
def client_fixture(some_config, requests_mock, fb_account_response):
    client = Client(**some_config)
    requests_mock.register_uri("GET", FacebookSession.GRAPH + "/v10.0/me/adaccounts", [fb_account_response])
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
def fb_account_response_fixture(account_id):
    return {
        "json": {
            "data": [
                {
                    "account_id": account_id,
                    "id": f"act_{account_id}",
                }
            ],
            "paging": {"cursors": {"before": "MjM4NDYzMDYyMTcyNTAwNzEZD", "after": "MjM4NDYzMDYyMTcyNTAwNzEZD"}},
        },
        "status_code": 200,
    }


class TestBackoff:
    def test_limit_reached(self, requests_mock, client, fb_call_rate_response, account_id):
        """Error once, check that we retry and not fail"""
        campaign_responses = [
            fb_call_rate_response,
            {
                "json": {"data": [{"id": 1, "updated_time": "2020-09-25T00:00:00Z"}, {"id": 2, "updated_time": "2020-09-25T00:00:00Z"}]},
                "status_code": 200,
            },
        ]

        requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/v10.0/act_{account_id}/campaigns", campaign_responses)
        requests_mock.register_uri("GET", FacebookSession.GRAPH + "/v10.0/1/", [{"status_code": 200}])
        requests_mock.register_uri("GET", FacebookSession.GRAPH + "/v10.0/2/", [{"status_code": 200}])

        records = list(client.read_stream(AirbyteStream(name="campaigns", json_schema={})))

        assert records

    def test_batch_limit_reached(self, requests_mock, client, fb_call_rate_response, account_id):
        """Error once, check that we retry and not fail"""
        responses = [
            fb_call_rate_response,
            {
                "json": {
                    "data": [
                        {
                            "id": "123",
                            "object_type": "SHARE",
                            "status": "ACTIVE",
                        },
                        {
                            "id": "1234",
                            "object_type": "SHARE",
                            "status": "ACTIVE",
                        },
                    ],
                    "status_code": 200,
                }
            },
        ]

        batch_responses = [
            fb_call_rate_response,
            {
                "json": [
                    {
                        "body": json.dumps({"name": "creative 1"}),
                        "code": 200,
                    },
                    {
                        "body": json.dumps({"name": "creative 2"}),
                        "code": 200,
                    },
                ]
            },
        ]

        requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/v10.0/act_{account_id}/adcreatives", responses)
        requests_mock.register_uri("POST", FacebookSession.GRAPH + "/v10.0/", batch_responses)

        records = list(client.read_stream(AirbyteStream(name="adcreatives", json_schema={})))

        assert records == [{"name": "creative 1"}, {"name": "creative 2"}]

    def test_server_error(self, requests_mock, client, account_id):
        """Error once, check that we retry and not fail"""
        responses = [
            {"json": {"error": {}}, "status_code": 500},
            {
                "json": {"data": [{"id": 1, "updated_time": "2020-09-25T00:00:00Z"}, {"id": 2, "updated_time": "2020-09-25T00:00:00Z"}]},
                "status_code": 200,
            },
        ]

        requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/v10.0/act_{account_id}/campaigns", responses)

        with pytest.raises(FacebookRequestError):
            list(client.read_stream(AirbyteStream(name="campaigns", json_schema={})))
