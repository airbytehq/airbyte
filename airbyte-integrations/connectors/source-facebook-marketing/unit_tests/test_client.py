#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import json
from datetime import datetime

import pendulum
import pytest
from airbyte_cdk.models import SyncMode
from facebook_business import FacebookAdsApi, FacebookSession
from facebook_business.exceptions import FacebookRequestError
from source_facebook_marketing.api import API
from source_facebook_marketing.streams import AdCreatives, Campaigns

FB_API_VERSION = FacebookAdsApi.API_VERSION


@pytest.fixture(scope="session", name="account_id")
def account_id_fixture():
    return "unknown_account"


@pytest.fixture(scope="session", name="some_config")
def some_config_fixture(account_id):
    return {"start_date": "2021-01-23T00:00:00Z", "account_id": f"{account_id}", "access_token": "unknown_token"}


@pytest.fixture(autouse=True)
def mock_default_sleep_interval(mocker):
    mocker.patch("source_facebook_marketing.common.DEFAULT_SLEEP_INTERVAL", return_value=pendulum.duration(seconds=5))


@pytest.fixture(name="api")
def api_fixture(some_config, requests_mock, fb_account_response):
    api = API(account_id=some_config["account_id"], access_token=some_config["access_token"])

    requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/me/adaccounts", [fb_account_response])
    return api


@pytest.fixture(name="fb_call_rate_response")
def fb_call_rate_response_fixture():
    error = {
        "message": "(#80000) There have been too many calls from this ad-account. Wait a bit and try again. For more info, please refer to https://developers.facebook.com/docs/graph-api/overview/rate-limiting.",
        "type": "OAuthException",
        "code": 80000,
        "error_subcode": 2446079,
        "fbtrace_id": "this_is_fake_response",
    }

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
    def test_limit_reached(self, requests_mock, api, fb_call_rate_response, account_id):
        """Error once, check that we retry and not fail"""
        campaign_responses = [
            fb_call_rate_response,
            {
                "json": {"data": [{"id": 1, "updated_time": "2020-09-25T00:00:00Z"}, {"id": 2, "updated_time": "2020-09-25T00:00:00Z"}]},
                "status_code": 200,
            },
        ]

        requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/act_{account_id}/campaigns", campaign_responses)
        requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/1/", [{"status_code": 200}])
        requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/2/", [{"status_code": 200}])

        stream = Campaigns(api=api, start_date=datetime.now(), include_deleted=False)
        try:
            records = list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_state={}))
            assert records
        except FacebookRequestError:
            pytest.fail("Call rate error has not being handled")

    def test_batch_limit_reached(self, requests_mock, api, fb_call_rate_response, account_id):
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
                    {"body": json.dumps({"name": "creative 1"}), "code": 200, "headers": {}},
                    {"body": json.dumps({"name": "creative 2"}), "code": 200, "headers": {}},
                ]
            },
        ]

        requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/act_{account_id}/adcreatives", responses)
        requests_mock.register_uri("POST", FacebookSession.GRAPH + f"/{FB_API_VERSION}/", batch_responses)

        stream = AdCreatives(api=api, include_deleted=False)
        records = list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_state={}))

        assert records == [{"name": "creative 1"}, {"name": "creative 2"}]

    def test_server_error(self, requests_mock, api, account_id):
        """Error once, check that we retry and not fail"""
        responses = [
            {"json": {"error": {}}, "status_code": 500},
            {
                "json": {"data": [{"id": 1, "updated_time": "2020-09-25T00:00:00Z"}, {"id": 2, "updated_time": "2020-09-25T00:00:00Z"}]},
                "status_code": 200,
            },
        ]

        requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/act_{account_id}/campaigns", responses)

        with pytest.raises(FacebookRequestError):
            stream = Campaigns(api=api, start_date=datetime.now(), include_deleted=False)
            list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_state={}))
