#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json

import pendulum
import pytest
import requests
from airbyte_cdk.models import SyncMode
from facebook_business import FacebookAdsApi, FacebookSession
from facebook_business.exceptions import FacebookRequestError
from source_facebook_marketing.streams import AdAccounts, Activities, AdCreatives, Campaigns, Videos

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
    error = {"message": "Please reduce the amount of data you're asking for, then retry your request", "code": 1}

    return {
        "json": {
            "error": error,
        },
        "status_code": 500,
    }


class TestBackoff:
    def test_limit_reached(self, source, mocker, requests_mock, api, fb_call_rate_response, account_id, second_account_id):
        """Error once, check that we retry and not fail"""
        # turn Campaigns into non batch mode to test non batch logic
        mocker.patch.object(Campaigns, "use_batch", new_callable=mocker.PropertyMock, return_value=False)
        campaign_responses = [
            fb_call_rate_response,
            {
                "json": {"data": [{"id": 1, "updated_time": "2020-09-25T00:00:00Z"}, {"id": 2, "updated_time": "2020-09-25T00:00:00Z"}]},
                "status_code": 200,
            },
        ]

        requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/act_{account_id}/campaigns", campaign_responses)
        requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/act_{second_account_id}/campaigns", campaign_responses)
        requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/1/", [{"status_code": 200}])
        requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/2/", [{"status_code": 200}])

        stream = Campaigns(source=source, api=api, start_date=pendulum.now(), end_date=pendulum.now(), include_deleted=False)
        try:
            records = list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_state={}))
            assert len(records) == 4
            assert [record["id"] for record in records] == [1, 2, 1, 2]
        except FacebookRequestError:
            pytest.fail("Call rate error has not being handled")

    def test_batch_limit_reached(self, source, requests_mock, api, fb_call_rate_response, account_id, second_account_id):
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
                    {"body": json.dumps({"name": "creative 1"}), "code": 200, "headers": {}},
                    {"body": json.dumps({"name": "creative 2"}), "code": 200, "headers": {}},
                ]
            },
        ]

        requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/act_{account_id}/adcreatives", responses)
        requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/act_{account_id}/", responses)
        requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/act_{second_account_id}/adcreatives", responses)
        requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/act_{second_account_id}/", responses)
        requests_mock.register_uri("POST", FacebookSession.GRAPH + f"/{FB_API_VERSION}/", batch_responses)

        stream = AdCreatives(source=source, api=api, include_deleted=False)
        records = list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_state={}))

        # Note for multi accounts: this test is kind of dumb as there's a lot of async involved and we mock batch response
        # data so everything else is useless. But it's usefull for debugging and yo CAN see that the elements in "response"
        # are sent twice to check the batch resonse stuff, so it does use 2 accounts
        assert records == [{"name": "creative 1"}, {"name": "creative 2"}, {"name": "creative 1"}, {"name": "creative 2"}]

    @pytest.mark.parametrize(
        "error_response",
        [
            {"json": {"error": {}}, "status_code": 500},
            {"json": {"error": {"code": 104}}},
            {"json": {"error": {"code": 2}}, "status_code": 500},
        ],
        ids=["server_error", "connection_reset_error", "temporary_oauth_error"],
    )
    def test_common_error_retry(self, source, mocker, error_response, requests_mock, api, account_id, second_account_id):
        """Error once, check that we retry and not fail"""
        account_data = {"id": 1, "updated_time": "2020-09-25T00:00:00Z", "name": "Some name"}
        second_account_data = {"id": 2, "updated_time": "2020-09-25T00:00:00Z", "name": "Some second name"}
        # do not test batch logic
        mocker.patch.object(AdAccounts, "use_batch", new_callable=mocker.PropertyMock, return_value=False)

        responses = [
            error_response,
            {
                "json": account_data,
                "status_code": 200,
            },
        ]

        second_account_responses = [
            error_response,
            {
                "json": second_account_data,
                "status_code": 200,
            },
        ]

        requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/me/business_users", json={"data": []})
        requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/act_{account_id}/", responses)
        requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/{account_data['id']}/", responses)
        requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/act_{second_account_id}/", second_account_responses)
        requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/{second_account_data['id']}/", second_account_responses)

        stream = AdAccounts(source=source, api=api)
        accounts = list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_state={}))

        assert accounts == [account_data, second_account_data]

    def test_limit_error_retry(self, source, fb_call_amount_data_response, requests_mock, api, account_id, second_account_id):
        """Error every time, check limit parameter decreases by 2 times every new call"""

        res = requests_mock.register_uri(
            "GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/act_{account_id}/campaigns", [fb_call_amount_data_response]
        )
        res_second_account = requests_mock.register_uri(
            "GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/act_{second_account_id}/campaigns", [fb_call_amount_data_response]
        )

        stream = Campaigns(source=source, api=api, start_date=pendulum.now(), end_date=pendulum.now(), include_deleted=False, page_size=100)
        try:
            list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_state={}))
        except FacebookRequestError:
            assert [x.qs.get("limit")[0] for x in res.request_history] == ["100", "50", "25", "12", "6", "3", "1", "1", '1', '1', '1', '1', '1', '1', '1']
            # we did get the second account because both queries are executed in parallel
            assert [x.qs.get("limit")[0] for x in res_second_account.request_history] == ['100', '50', '25', '12', '6', '3', '1', '1', '1', '1', '1', '1', '1', '1', '1']

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
                'data': [],
                "paging": {
                    "cursors": {
                        "after": "test",
                    },
                    "next": f"https://graph.facebook.com/{FB_API_VERSION}/act_{account_id}/activities?limit=31&after=test"
                }
            },
            "status_code": 200,
        }

        res = requests_mock.register_uri(
            "GET",
            FacebookSession.GRAPH + f"/{FB_API_VERSION}/act_{account_id}/activities",
            [error, success, error, success],
        )

        stream = Activities(api=api, start_date=pendulum.now(), end_date=pendulum.now(), include_deleted=False, page_size=100)
        try:
            list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_state={}))
        except FacebookRequestError:
            assert [x.qs.get("limit")[0] for x in res.request_history] == ['100', '50', '100', '50']

    def test_limit_error_retry_next_page(self, source, fb_call_amount_data_response, requests_mock, api, account_id, second_account_id):
        """Unlike the previous test, this one tests the API call fail on the second or more page of a request."""
        base_url = FacebookSession.GRAPH + f"/{FB_API_VERSION}/act_{account_id}/advideos"
        base_url_second_account = FacebookSession.GRAPH + f"/{FB_API_VERSION}/act_{second_account_id}/advideos"

        api_resonse = [
            {
                "json": {
                    "data": [{"id": 1, "updated_time": "2020-09-25T00:00:00Z"}, {"id": 2, "updated_time": "2020-09-25T00:00:00Z"}],
                    "paging": {"next": f"{base_url}?after=after_page_1&limit=100"}
                },
                "status_code": 200
            },
            fb_call_amount_data_response
        ]

        res = requests_mock.register_uri( "GET", base_url, api_resonse)
        res_second_account = requests_mock.register_uri( "GET", base_url_second_account, api_resonse)

        stream = Videos(source=source, api=api, start_date=pendulum.now(), end_date=pendulum.now(), include_deleted=False, page_size=100)
        try:
            list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_state={}))
        except FacebookRequestError:
            assert [x.qs.get("limit")[0] for x in res.request_history] == ["100", "100", "50", "25", "12", "6", "3", "1", "1", "1", "1", "1", "1", "1", "1", "1"]
            # we got the first page for both of them, but the second page triggered error in the first account so the second didn't get its chance
            assert [x.qs.get("limit")[0] for x in res_second_account.request_history] == ["100"]
