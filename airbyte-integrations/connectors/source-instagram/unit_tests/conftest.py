#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from facebook_business import FacebookAdsApi, FacebookSession
from pytest import fixture
from source_instagram.api import InstagramAPI as API

FB_API_VERSION = FacebookAdsApi.API_VERSION


@fixture(scope="session", name="account_id")
def account_id_fixture():
    return "unknown_account"


@fixture(name="config")
def config_fixture():
    config = {
        "access_token": "TOKEN",
        "start_date": "2022-03-20T00:00:00",
    }

    return config


@fixture(scope="session", name="some_config")
def some_config_fixture(account_id):
    return {"start_date": "2021-01-23T00:00:00Z", "access_token": "unknown_token"}


@fixture(name="fb_account_response")
def fb_account_response_fixture(account_id, some_config, requests_mock):
    account = {"id": "test_id", "instagram_business_account": {"id": "test_id"}}
    requests_mock.register_uri(
        "GET",
        FacebookSession.GRAPH + f"/{FB_API_VERSION}/act_{account_id}/"
        f"?access_token={some_config['access_token']}&fields=instagram_business_account",
        json=account,
    )
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


@fixture(name="api")
def api_fixture(some_config, requests_mock, fb_account_response):
    api = API(access_token=some_config["access_token"])

    requests_mock.register_uri(
        "GET",
        FacebookSession.GRAPH + f"/{FB_API_VERSION}/me/accounts?" f"access_token={some_config['access_token']}&summary=true",
        [fb_account_response],
    )

    return api


@fixture(name="user_data")
def user_data_fixture():
    return {
        "biography": "Dino data crunching app",
        "id": "17841405822304914",
        "username": "metricsaurus",
        "website": "http://www.metricsaurus.com/",
    }


@fixture(name="user_insight_data")
def user_insight_data_fixture():
    return {
        "name": "impressions",
        "period": "day",
        "values": [{"value": 4, "end_time": "2020-05-04T07:00:00+0000"}, {"value": 66, "end_time": "2020-05-05T07:00:00+0000"}],
        "title": "Impressions",
        "description": "Total number of times this profile has been seen",
        "id": "17841400008460056/insights/impressions/day",
    }


@fixture(name="user_stories_data")
def user_stories_data_fixture():
    return {"id": "test_id"}


@fixture(name="user_media_insights_data")
def user_media_insights_data_fixture():
    return {
        "name": "impressions",
        "period": "lifetime",
        "values": [{"value": 264}],
        "title": "Impressions",
        "description": "Total number of times the media object has been seen",
        "id": "17855590849148465/insights/impressions/lifetime",
    }
