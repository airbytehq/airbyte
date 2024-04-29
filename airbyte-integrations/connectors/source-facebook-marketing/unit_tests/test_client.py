#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json

import pendulum
import pytest
from airbyte_cdk.models import SyncMode
from airbyte_cdk.utils import AirbyteTracedException
from airbyte_protocol.models import FailureType
from facebook_business import FacebookAdsApi, FacebookSession
from facebook_business.exceptions import FacebookRequestError
from source_facebook_marketing.streams import Activities, AdAccount, AdCreatives, Campaigns, Videos

FB_API_VERSION = FacebookAdsApi.API_VERSION


@pytest.fixture(name="fb_call_rate_response")
def fb_call_rate_response_fixture():
    error = {
        "message": (
            "(#80000) There have been too many calls from this ad-account. Wait a bit and try again. "
            "For more info, please refer to https://developers.facebook.com/docs/graph-api/overview/rate-limiting."
        ),
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


@pytest.fixture(name="fb_call_amount_data_response")
def fb_call_amount_data_response_fixture():
    error = {
        "message": "Please reduce the amount of data you're asking for, then retry your request",
        "code": 1,
    }

    return {
        "json": {
            "error": error,
        },
        "status_code": 500,
    }


class TestBackoff:
    def test_limit_reached(self, mocker, requests_mock, api, fb_call_rate_response, account_id, some_config):
        """Error once, check that we retry and not fail"""
        # turn Campaigns into non batch mode to test non batch logic
        campaign_responses = [
            fb_call_rate_response,
            {
                "json": {
                    "data": [
                        {"id": 1, "updated_time": "2020-09-25T00:00:00Z"},
                        {"id": 2, "updated_time": "2020-09-25T00:00:00Z"},
                    ]
                },
                "status_code": 200,
            },
        ]

        requests_mock.register_uri(
            "GET",
            FacebookSession.GRAPH + f"/{FB_API_VERSION}/act_{account_id}/campaigns",
            campaign_responses,
        )
        requests_mock.register_uri(
            "GET",
            FacebookSession.GRAPH + f"/{FB_API_VERSION}/1/",
            [{"status_code": 200}],
        )
        requests_mock.register_uri(
            "GET",
            FacebookSession.GRAPH + f"/{FB_API_VERSION}/2/",
            [{"status_code": 200}],
        )

        stream = Campaigns(
            api=api,
            account_ids=[account_id],
            start_date=pendulum.now(),
            end_date=pendulum.now(),
        )
        try:
            records = list(
                stream.read_records(
                    sync_mode=SyncMode.full_refresh,
                    stream_state={},
                    stream_slice={"account_id": account_id},
                )
            )
            assert records
        except FacebookRequestError:
            pytest.fail("Call rate error has not being handled")

    def test_given_rate_limit_reached_when_read_then_raise_transient_traced_exception(self, requests_mock, api, fb_call_rate_response, account_id, some_config):
        requests_mock.register_uri(
            "GET",
            FacebookSession.GRAPH + f"/{FB_API_VERSION}/act_{account_id}/campaigns",
            [fb_call_rate_response],
        )

        stream = Campaigns(
            api=api,
            account_ids=[account_id],
            start_date=pendulum.now(),
            end_date=pendulum.now(),
        )

        with pytest.raises(AirbyteTracedException) as exception:
            list(
                stream.read_records(
                    sync_mode=SyncMode.full_refresh,
                    stream_state={},
                    stream_slice={"account_id": account_id},
                )
            )

        assert exception.value.failure_type == FailureType.transient_error

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
                    {
                        "body": json.dumps({"name": "creative 1"}),
                        "code": 200,
                        "headers": {},
                    },
                    {
                        "body": json.dumps({"name": "creative 2"}),
                        "code": 200,
                        "headers": {},
                    },
                ]
            },
        ]

        requests_mock.register_uri(
            "GET",
            FacebookSession.GRAPH + f"/{FB_API_VERSION}/act_{account_id}/adcreatives",
            responses,
        )
        requests_mock.register_uri(
            "GET",
            FacebookSession.GRAPH + f"/{FB_API_VERSION}/act_{account_id}/",
            responses,
        )
        requests_mock.register_uri("POST", FacebookSession.GRAPH + f"/{FB_API_VERSION}/", batch_responses)

        stream = AdCreatives(api=api, account_ids=[account_id])
        records = list(
            stream.read_records(
                sync_mode=SyncMode.full_refresh,
                stream_state={},
                stream_slice={"account_id": account_id},
            )
        )

        assert records == [
            {
                "account_id": "unknown_account",
                "id": "123",
                "object_type": "SHARE",
                "status": "ACTIVE",
            },
            {
                "account_id": "unknown_account",
                "id": "1234",
                "object_type": "SHARE",
                "status": "ACTIVE",
            },
        ]

    @pytest.mark.parametrize(
        "error_response",
        [
            {"json": {"error": {}}, "status_code": 500},
            {"json": {"error": {"code": 104}}},
            {"json": {"error": {"code": 2}}, "status_code": 500},
        ],
        ids=["server_error", "connection_reset_error", "temporary_oauth_error"],
    )
    def test_common_error_retry(self, error_response, requests_mock, api, account_id):
        """Error once, check that we retry and not fail"""
        account_data = {
            "account_id": "unknown_account",
            "id": 1,
            "updated_time": "2020-09-25T00:00:00Z",
            "name": "Some name",
        }
        responses = [
            error_response,
            {
                "json": account_data,
                "status_code": 200,
            },
        ]

        requests_mock.register_uri(
            "GET",
            FacebookSession.GRAPH + f"/{FB_API_VERSION}/me/business_users",
            json={"data": []},
        )
        requests_mock.register_uri(
            "GET",
            FacebookSession.GRAPH + f"/{FB_API_VERSION}/act_{account_id}/",
            responses,
        )
        requests_mock.register_uri(
            "GET",
            FacebookSession.GRAPH + f"/{FB_API_VERSION}/{account_data['id']}/",
            responses,
        )

        stream = AdAccount(api=api, account_ids=[account_id])
        accounts = list(
            stream.read_records(
                sync_mode=SyncMode.full_refresh,
                stream_state={},
                stream_slice={"account_id": account_id},
            )
        )

        assert accounts == [account_data]

    def test_limit_error_retry(self, fb_call_amount_data_response, requests_mock, api, account_id):
        """Error every time, check limit parameter decreases by 2 times every new call"""

        res = requests_mock.register_uri(
            "GET",
            FacebookSession.GRAPH + f"/{FB_API_VERSION}/act_{account_id}/campaigns",
            [fb_call_amount_data_response],
        )

        stream = Campaigns(
            api=api,
            account_ids=[account_id],
            start_date=pendulum.now(),
            end_date=pendulum.now(),
            page_size=100,
        )
        try:
            list(
                stream.read_records(
                    sync_mode=SyncMode.full_refresh,
                    stream_state={},
                    stream_slice={"account_id": account_id},
                )
            )
        except AirbyteTracedException:
            assert [x.qs.get("limit")[0] for x in res.request_history] == [
                "100",
                "50",
                "25",
                "12",
                "6",
            ]

    def test_limit_error_retry_revert_page_size(self, requests_mock, api, account_id):
        """Error every time, check limit parameter decreases by 2 times every new call"""

        error = {
            "json": {
                "error": {
                    "message": "An unknown error occurred",
                    "code": 1,
                }
            },
            "status_code": 500,
        }
        success = {
            "json": {
                "data": [],
                "paging": {
                    "cursors": {
                        "after": "test",
                    },
                    "next": f"https://graph.facebook.com/{FB_API_VERSION}/act_{account_id}/activities?limit=31&after=test",
                },
            },
            "status_code": 200,
        }

        res = requests_mock.register_uri(
            "GET",
            FacebookSession.GRAPH + f"/{FB_API_VERSION}/act_{account_id}/activities",
            [error, success, error, success],
        )

        stream = Activities(
            api=api,
            account_ids=[account_id],
            start_date=pendulum.now(),
            end_date=pendulum.now(),
            page_size=100,
        )
        try:
            list(
                stream.read_records(
                    sync_mode=SyncMode.full_refresh,
                    stream_state={},
                    stream_slice={"account_id": account_id},
                )
            )
        except FacebookRequestError:
            assert [x.qs.get("limit")[0] for x in res.request_history] == [
                "100",
                "50",
                "100",
                "50",
            ]

    def test_start_date_not_provided(self, requests_mock, api, account_id):
        success = {
            "json": {
                "data": [],
                "paging": {
                    "cursors": {
                        "after": "test",
                    },
                    "next": f"https://graph.facebook.com/{FB_API_VERSION}/act_{account_id}/activities?limit=31&after=test",
                },
            },
            "status_code": 200,
        }

        requests_mock.register_uri(
            "GET",
            FacebookSession.GRAPH + f"/{FB_API_VERSION}/act_{account_id}/activities",
            [success],
        )

        stream = Activities(
            api=api,
            account_ids=[account_id],
            start_date=None,
            end_date=None,
            page_size=100,
        )
        list(
            stream.read_records(
                sync_mode=SyncMode.full_refresh,
                stream_state={},
                stream_slice={"account_id": account_id},
            )
        )

    def test_limit_error_retry_next_page(self, fb_call_amount_data_response, requests_mock, api, account_id):
        """Unlike the previous test, this one tests the API call fail on the second or more page of a request."""
        base_url = FacebookSession.GRAPH + f"/{FB_API_VERSION}/act_{account_id}/advideos"

        res = requests_mock.register_uri(
            "GET",
            base_url,
            [
                {
                    "json": {
                        "data": [
                            {"id": 1, "updated_time": "2020-09-25T00:00:00Z"},
                            {"id": 2, "updated_time": "2020-09-25T00:00:00Z"},
                        ],
                        "paging": {"next": f"{base_url}?after=after_page_1&limit=100"},
                    },
                    "status_code": 200,
                },
                fb_call_amount_data_response,
            ],
        )

        stream = Videos(
            api=api,
            account_ids=[account_id],
            start_date=pendulum.now(),
            end_date=pendulum.now(),
            page_size=100,
        )
        try:
            list(
                stream.read_records(
                    sync_mode=SyncMode.full_refresh,
                    stream_state={},
                    stream_slice={"account_id": account_id},
                )
            )
        except AirbyteTracedException:
            assert [x.qs.get("limit")[0] for x in res.request_history] == [
                "100",
                "100",
                "50",
                "25",
                "12",
                "6",
            ]
