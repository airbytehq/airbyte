#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import timedelta

from facebook_business import FacebookAdsApi, FacebookSession
from pytest import fixture
from source_facebook_marketing.api import API


FB_API_VERSION = FacebookAdsApi.API_VERSION


@fixture(autouse=True)
def time_sleep_mock(mocker):
    time_mock = mocker.patch("time.sleep")
    yield time_mock


@fixture(scope="session", name="account_id")
def account_id_fixture():
    return "unknown_account"


@fixture(scope="session", name="some_config")
def some_config_fixture(account_id):
    return {
        "start_date": "2021-01-23T00:00:00Z",
        "account_ids": [f"{account_id}"],
        "access_token": "unknown_token",
    }


@fixture(autouse=True)
def mock_default_sleep_interval(mocker):
    mocker.patch(
        "source_facebook_marketing.streams.common.DEFAULT_SLEEP_INTERVAL",
        return_value=timedelta(seconds=5),
    )


@fixture(name="fb_account_response")
def fb_account_response_fixture(account_id):
    return {
        "json": {
            "data": [
                {
                    "account_id": account_id,
                    "id": f"act_{account_id}",
                }
            ],
            "paging": {
                "cursors": {
                    "before": "MjM4NDYzMDYyMTcyNTAwNzEZD",
                    "after": "MjM4NDYzMDYyMTcyNTAwNzEZD",
                }
            },
        },
        "status_code": 200,
    }


@fixture(name="api")
def api_fixture(some_config, requests_mock, fb_account_response):
    api = API(access_token=some_config["access_token"], page_size=100)

    requests_mock.register_uri(
        "GET",
        FacebookSession.GRAPH + f"/{FB_API_VERSION}/me/adaccounts",
        [fb_account_response],
    )
    requests_mock.register_uri(
        "GET",
        FacebookSession.GRAPH + f"/{FB_API_VERSION}/act_{some_config['account_ids'][0]}/",
        [fb_account_response],
    )
    return api


@fixture(name="config")
def config_fixture(requests_mock):
    config = {
        "account_ids": ["123"],
        "access_token": "ACCESS_TOKEN",
        "credentials": {
            "auth_type": "Service",
            "access_token": "ACCESS_TOKEN",
        },
        "start_date": "2019-10-10T00:00:00Z",
        "end_date": "2020-10-10T00:00:00Z",
    }
    requests_mock.register_uri(
        "GET",
        FacebookSession.GRAPH + f"/{FacebookAdsApi.API_VERSION}/me/business_users",
        json={"data": []},
    )
    requests_mock.register_uri(
        "GET",
        FacebookSession.GRAPH + f"/{FacebookAdsApi.API_VERSION}/act_123/",
        json={"account": 123},
    )
    return config
