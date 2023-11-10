#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pendulum
from facebook_business import FacebookAdsApi, FacebookSession
from pytest import fixture
from source_facebook_marketing.api import API

FB_API_VERSION = FacebookAdsApi.API_VERSION


@fixture(autouse=True)
def time_sleep_mock(mocker):
    time_mock = mocker.patch("time.sleep")
    yield time_mock


@fixture(scope="session", name="account_id_1")
def account_id_1_fixture():
    return "unknown_account"

@fixture(scope="session", name="account_id_2")
def account_id_2_fixture():
    return "unknown_account"

@fixture(scope="session", name="some_config")
def some_config_fixture(account_id_1, account_id_2):
    return {"start_date": "2021-01-23T00:00:00Z", "account_ids": f"{account_id_1},{account_id_2}", "access_token": "unknown_token"}


@fixture(autouse=True)
def mock_default_sleep_interval(mocker):
    mocker.patch("source_facebook_marketing.streams.common.DEFAULT_SLEEP_INTERVAL", return_value=pendulum.duration(seconds=5))


@fixture(name="fb_account_response")
def fb_account_response_fixture(account_id_1, account_id_2):
    return {
            account_id_1: {
            "json": {
                "data": [
                    {
                        "account_id": account_id_1,
                        "id": f"act_{account_id_1}",
                    }
                ],
                "paging": {"cursors": {"before": "MjM4NDYzMDYyMTcyNTAwNzEZD", "after": "MjM4NDYzMDYyMTcyNTAwNzEZD"}},
            },
            "status_code": 200,
            },
            account_id_2: {
                "json": {
                    "data": [
                        {
                            "account_id": account_id_2,
                            "id": f"act_{account_id_2}",
                        }
                    ],
                    "paging": {"cursors": {"before": "MjM4NDYzMDYyMTcyNTAwNzEZD", "after": "MjM4NDYzMDYyMTcyNTAwNzEZD"}},
                },
                "status_code": 200,
            }
        }


@fixture(name="api")
def api_fixture(some_config, requests_mock, fb_account_response):
    api = API(account_ids=some_config["account_ids"], access_token=some_config["access_token"], page_size=100)

    requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/me/adaccounts", [fb_account_response])
    for account_id in some_config['account_ids'].split(','):
        requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/act_{account_id}/", [fb_account_response[account_id]])
    return api
