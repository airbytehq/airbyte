#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from datetime import datetime

from unittest.mock import MagicMock
import pytest
from source_instagram.streams import InstagramStream, Users, UserInsights
from airbyte_cdk.models import SyncMode
from facebook_business import FacebookAdsApi, FacebookSession


FB_API_VERSION = FacebookAdsApi.API_VERSION


@pytest.mark.parametrize(
    "error_response",
    [
        {"json": {"error": {}}, "status_code": 500},
        {"json": {"error": {"code": 104}}},
        {"json": {"error": {"code": 2}}, "status_code": 500},
    ],
    ids=["server_error", "connection_reset_error", "temporary_oauth_error"],
)
def test_common_error_retry(error_response, requests_mock, api, account_id, some_config):
    """Error once, check that we retry and not fail"""
    account_data = {'page_id': 'test_id'}
    responses = [
        error_response,
    ]

    requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/me/accounts?access_token={some_config['access_token']}&summary=true", responses)

    stream = Users(api=api)

    instagram_business_account = MagicMock()
    instagram_business_account.api_get = MagicMock()
    instagram_business_account.api_get().export_all_data = MagicMock(return_value={"page_id": "123"})

    accounts = list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_state={}, stream_slice={"account": {
        "page_id": "test_id",
        "instagram_business_account": instagram_business_account
    }}))

    assert accounts == [account_data]


def test_clear_url(config):
    media_url = "https://google.com?_nc_rid=123"
    profile_picture_url = "https://google.com?ccb=123"

    expected = {"media_url": "https://google.com", "profile_picture_url": "https://google.com"}
    assert InstagramStream._clear_url({"media_url": media_url, "profile_picture_url": profile_picture_url}) == expected


def test_state_outdated(api, config):
    assert UserInsights(api=api, start_date=datetime.strptime(config["start_date"], "%Y-%m-%dT%H:%M:%S"))._state_has_legacy_format({"state": MagicMock()})


def test_state_is_not_outdated(api, config):
    assert not UserInsights(api=api, start_date=datetime.strptime(config["start_date"], "%Y-%m-%dT%H:%M:%S"))._state_has_legacy_format({"state": {}})
