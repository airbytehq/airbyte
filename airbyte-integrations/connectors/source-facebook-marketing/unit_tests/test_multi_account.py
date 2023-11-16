import itertools

import pendulum
import pytest

from airbyte_cdk.models import SyncMode
from facebook_business import FacebookAdsApi, FacebookSession
from facebook_business.adobjects.ad import Ad
from source_facebook_marketing.api import API, AdAccount

from source_facebook_marketing.streams import Ads, Activities, AdCreatives, Campaigns, Videos, AdSets, CustomConversions, CustomAudiences, \
    Images, AdsInsights

FB_API_VERSION = FacebookAdsApi.API_VERSION


@pytest.fixture(scope="session", name="other_account_id")
def other_account_id_fixture():
    return "other_unknown_account"


@pytest.fixture(scope="session", name="multi_account_config")
def multi_account_config_fixture(account_id, other_account_id):
    return {"start_date": "2021-01-23T00:00:00Z", "account_ids": f"{account_id},{other_account_id}", "access_token": "unknown_token"}


@pytest.fixture(name="multi_account_api")
def api_fixture(multi_account_config, requests_mock, fb_account_response):
    accounts = multi_account_config['account_ids'].split(',')
    api = API(account_ids=accounts, access_token=multi_account_config["access_token"], page_size=100)

    requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/me/adaccounts", [fb_account_response])
    for account_id in accounts:
        requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/act_{account_id}/", [{
            "json": {
                "data": [
                    {
                        "account_id": account_id,
                        "id": f"act_{account_id}",
                    }
                ],
                "paging": {"cursors": {"before": "MjM4NDYzMDYyMTcyNTAwNzEZD", "after": "MjM4NDYzMDYyMTcyNTAwNzEZD"}},
            },
        }])
    return api


class TestMultiAccount:
    def test_get_multiple_accounts(self, multi_account_api, account_id, other_account_id):
        for account in multi_account_api.accounts:
            assert isinstance(account, AdAccount)
        assert [account_id, other_account_id] == [account.get_id() for account in multi_account_api.accounts]

    @pytest.mark.parametrize("route, stream_class, kwargs", [
        ("activities", Activities, {"start_date": pendulum.now(), "end_date": pendulum.now(), "include_deleted": False, "page_size": 100}),
        ("adcreatives", AdCreatives, {"include_deleted": False, "page_size": 100}),
        ("adimages", Images,
         {"start_date": pendulum.now(), "end_date": pendulum.now(), "include_deleted": False, "page_size": 100}),
        ("ads", Ads, {"start_date": pendulum.now(), "end_date": pendulum.now(), "include_deleted": False, "page_size": 100}),
        ("adsets", AdSets, {"start_date": pendulum.now(), "end_date": pendulum.now(), "include_deleted": False, "page_size": 100}),
        ("advideos", Videos, {"start_date": pendulum.now(), "end_date": pendulum.now(), "include_deleted": False, "page_size": 100}),
        ("campaigns", Campaigns, {"start_date": pendulum.now(), "end_date": pendulum.now(), "include_deleted": False, "page_size": 100}),
        ("customconversions", CustomConversions, {"include_deleted": False, "page_size": 100}),
        ("customaudiences", CustomAudiences, {"include_deleted": False, "page_size": 100})
    ])
    def test_get_multiple_accounts_streams(self, requests_mock, multi_account_api, account_id, other_account_id, route, stream_class,
                                           kwargs):
        base_url = FacebookSession.GRAPH + f"/{FB_API_VERSION}"
        expected = {
            account_id: [
                {"id": 1, "updated_time": "2020-09-25T00:00:00Z", "status": "active"},
                {"id": 2, "updated_time": "2020-09-25T00:00:00Z", "status": "active"}],
            other_account_id: [
                {"id": 3, "updated_time": "2020-09-25T00:00:00Z", "status": "active"},
                {"id": 4, "updated_time": "2020-09-25T00:00:00Z", "status": "active"}]
        }
        for act in [account_id, other_account_id]:
            requests_mock.register_uri(
                "GET",
                f"{base_url}/act_{act}/{route}",
                [
                    {
                        "json": {
                            "data": expected[act]
                        },
                        "status_code": 200,
                    }
                ]
            )

        stream = stream_class(api=multi_account_api, **kwargs)
        objects = list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_state={}))

        assert list(itertools.chain(*expected.values())) == objects
