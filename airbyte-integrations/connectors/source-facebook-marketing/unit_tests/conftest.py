#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pendulum
from facebook_business import FacebookAdsApi, FacebookSession
from pytest import fixture
from source_facebook_marketing.api import API
from facebook_business.adobjects.adaccount import AdAccount

FB_API_VERSION = FacebookAdsApi.API_VERSION

@fixture(autouse=True)
def time_sleep_mock(mocker):
    time_mock = mocker.patch("time.sleep")
    yield time_mock


@fixture(name="source")
def source_fixture(mocker):
    source = mocker.Mock()
    source.name = "source name"
    return source


@fixture(scope="session", name="account_id")
def account_id_fixture():
    return "unknown_account"

@fixture(scope="session", name="second_account_id")
def second_account_id_fixture():
    return "second_unknown_account"

@fixture(scope="session", name="some_config")
def some_config_fixture(account_id):
    return {"start_date": "2021-01-23T00:00:00Z", "account_id": f"{account_id}", "access_token": "unknown_token"}

@fixture(scope="session", name="some_second_config")
def some_second_config_fixture(second_account_id):
    return {"start_date": "2021-01-23T00:00:00Z", "account_id": f"{second_account_id}", "access_token": "unknown_token"}

@fixture(autouse=True)
def mock_default_sleep_interval(mocker):
    mocker.patch("source_facebook_marketing.streams.common.DEFAULT_SLEEP_INTERVAL", return_value=pendulum.duration(seconds=5))


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
            "paging": {"cursors": {"before": "MjM4NDYzMDYyMTcyNTAwNzEZD", "after": "MjM4NDYzMDYyMTcyNTAwNzEZD"}},
            "something_else": {"cursors": {"before": "MjM4NDYzMDYyMTcyNTAwNzEZD", "after": "MjM4NDYzMDYyMTcyNTAwNzEZD"}}
        },
        "status_code": 200,
    }

@fixture(name="second_fb_account_response")
def second_fb_account_response_fixture(second_account_id):
    return {
        "json": {
            "data": [
                {
                    "account_id": second_account_id,
                    "id": f"act_{second_account_id}",
                }
            ],
            "paging": {"cursors": {"before": "MjM4NDYzMDYyMTcyNTAwNzEZD", "after": "MjM4NDYzMDYyMTcyNTAwNzEZD"}},
            "something_else": {"cursors": {"before": "MjM4NDYzMDYyMTcyNTAwNzEZD", "after": "MjM4NDYzMDYyMTcyNTAwNzEZD"}}
        },
        "status_code": 200,
    }


@fixture(name="api")
def api_fixture(some_config, some_second_config, requests_mock, fb_account_response, second_fb_account_response):
    api = API(account_ids=[some_config["account_id"], some_second_config["account_id"]], access_token=some_config["access_token"], page_size=100)

    requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/me/adaccounts", [fb_account_response])
    requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/act_{some_config['account_id']}/", [fb_account_response])
    requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/act_{some_second_config['account_id']}/", [second_fb_account_response])
    return api

