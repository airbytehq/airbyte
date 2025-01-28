#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, Dict, List

import pytest
import requests
from conftest import find_stream, get_source, load_json_file
from source_linkedin_ads.source import SourceLinkedinAds

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator, TokenAuthenticator


logger = logging.getLogger("airbyte")

LINKEDIN_VERSION_API = 202404

TEST_OAUTH_CONFIG: dict = {
    "start_date": "2021-08-01",
    "account_ids": [],
    "credentials": {
        "auth_method": "oAuth2.0",
        "client_id": "client_id",
        "client_secret": "client_secret",
        "refresh_token": "refresh_token",
    },
}

TEST_CONFIG: dict = {
    "start_date": "2021-01-01",
    "end_date": "2021-02-01",
    "account_ids": [1, 2],
    "credentials": {
        "auth_method": "access_token",
        "access_token": "access_token",
        "authenticator": TokenAuthenticator(token="123"),
    },
}

TEST_CONFIG_DUPLICATE_CUSTOM_AD_ANALYTICS_REPORTS: dict = {
    "start_date": "2021-01-01",
    "account_ids": [],
    "credentials": {
        "auth_method": "oAuth2.0",
        "client_id": "client_id",
        "client_secret": "client_secret",
        "refresh_token": "refresh_token",
    },
    "ad_analytics_reports": [
        {"name": "ShareAdByMonth", "pivot_by": "COMPANY", "time_granularity": "MONTHLY"},
        {"name": "ShareAdByMonth", "pivot_by": "COMPANY", "time_granularity": "MONTHLY"},
    ],
}


class TestAllStreams:
    @pytest.fixture
    def linkedin_source(self) -> SourceLinkedinAds:
        return get_source(TEST_CONFIG)

    @staticmethod
    def _mock_initialize_cache_for_parent_streams(stream_configs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        parent_streams = set()

        def update_with_cache_parent_configs(parent_configs: list[dict[str, Any]]) -> None:
            for parent_config in parent_configs:
                parent_streams.add(parent_config["stream"]["name"])
                parent_config["stream"]["retriever"]["requester"]["use_cache"] = False

        for stream_config in stream_configs:
            if stream_config.get("incremental_sync", {}).get("parent_stream"):
                parent_streams.add(stream_config["incremental_sync"]["parent_stream"]["name"])
                stream_config["incremental_sync"]["parent_stream"]["retriever"]["requester"]["use_cache"] = False

            elif stream_config.get("retriever", {}).get("partition_router", {}):
                partition_router = stream_config["retriever"]["partition_router"]

                if isinstance(partition_router, dict) and partition_router.get("parent_stream_configs"):
                    update_with_cache_parent_configs(partition_router["parent_stream_configs"])
                elif isinstance(partition_router, list):
                    for router in partition_router:
                        if router.get("parent_stream_configs"):
                            update_with_cache_parent_configs(router["parent_stream_configs"])

        for stream_config in stream_configs:
            if stream_config["name"] in parent_streams:
                stream_config["retriever"]["requester"]["use_cache"] = False

        return stream_configs

    @pytest.mark.parametrize("error_code", [429, 500, 503])
    def test_should_retry_on_error(self, error_code, requests_mock, mocker):
        mocker.patch.object(
            ManifestDeclarativeSource, "_initialize_cache_for_parent_streams", side_effect=self._mock_initialize_cache_for_parent_streams
        )
        mocker.patch("time.sleep", lambda x: None)
        stream = find_stream("accounts", TEST_CONFIG)
        requests_mock.register_uri(
            "GET", "https://api.linkedin.com/rest/adAccounts", [{"status_code": error_code, "json": {"elements": []}}]
        )
        stream.exit_on_rate_limit = True
        with pytest.raises(DefaultBackoffException):
            list(stream.read_records(sync_mode=SyncMode.full_refresh))

    def test_custom_streams(self, requests_mock):
        config = {"ad_analytics_reports": [{"name": "ShareAdByMonth", "pivot_by": "COMPANY", "time_granularity": "MONTHLY"}], **TEST_CONFIG}
        streams = get_source(config).streams(config=config)
        custom_streams = [stream for stream in streams if "custom_" in stream.name]

        assert len(custom_streams) == 1

        custom_stream = custom_streams[0]
        requests_mock.get("https://api.linkedin.com/rest/adAccounts", json={"elements": [{"id": 1}]})
        requests_mock.get(
            "https://api.linkedin.com/rest/adAccounts/1/adCampaigns?q=search&search=(status:(values:List(ACTIVE,PAUSED,ARCHIVED,"
            "COMPLETED,CANCELED,DRAFT,PENDING_DELETION,REMOVED)))",
            json={"elements": [{"id": 1111, "lastModified": "2021-01-15"}]},
        )
        requests_mock.get(
            "https://api.linkedin.com/rest/adAnalytics?q=analytics&pivot=(value:COMPANY)&timeGranularity=(value:MONTHLY)&campaigns=List("
            "urn%3Ali%3AsponsoredCampaign%3A1111)&dateRange=(start:(year:2021,month:1,day:1),end:(year:2021,month:1,day:31))",
            [
                {"json": load_json_file("responses/ad_member_country_analytics/response_1.json")},
                {"json": load_json_file("responses/ad_member_country_analytics/response_2.json")},
                {"json": load_json_file("responses/ad_member_country_analytics/response_3.json")},
            ],
        )

        stream_slice = next(custom_stream.stream_slices(sync_mode=SyncMode.full_refresh))
        records = list(custom_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice, stream_state=None))

        assert len(records) == 2

    @pytest.mark.parametrize(
        "stream_name, expected",
        [
            ("accounts", "adAccounts"),
            ("account_users", "adAccountUsers"),
            ("campaign_groups", "adAccounts/{{stream_slice.get('account_id')}}/adCampaignGroups"),
            ("campaigns", "adAccounts/{{stream_slice.get('account_id')}}/adCampaigns"),
            ("creatives", "adAccounts/{{stream_slice.get('account_id')}}/creatives"),
            ("ad_campaign_analytics", "adAnalytics"),
            ("ad_creative_analytics", "adAnalytics"),
        ],
        ids=[
            "Accounts",
            "AccountUsers",
            "CampaignGroups",
            "Campaigns",
            "Creatives",
            "AdCampaignAnalytics",
            "AdCreativeAnalytics",
        ],
    )
    def test_path(self, stream_name, expected):
        stream = find_stream(stream_name, config=TEST_CONFIG)
        result = stream.retriever.requester.path
        assert result == expected

    @pytest.mark.parametrize(
        ("status_code", "is_connection_successful", "error_msg"),
        (
            (
                400,
                False,
                ("Bad request. Please check your request parameters."),
            ),
            (
                403,
                False,
                ("Forbidden. You don't have permission to access this resource."),
            ),
            (200, True, None),
        ),
    )
    def test_check_connection(self, requests_mock, linkedin_source, status_code, is_connection_successful, error_msg, mocker):
        mocker.patch.object(
            ManifestDeclarativeSource, "_initialize_cache_for_parent_streams", side_effect=self._mock_initialize_cache_for_parent_streams
        )
        mocker.patch("time.sleep", lambda x: None)
        json = {"elements": [{"data": []}] * 500} if 200 >= status_code < 300 else {}
        requests_mock.register_uri(
            "GET",
            "https://api.linkedin.com/rest/adAccounts?q=search&pageSize=500",
            status_code=status_code,
            json=json,
        )
        success, error = linkedin_source.check_connection(logger=logger, config=TEST_CONFIG)
        assert success is is_connection_successful
        assert error == error_msg


class TestLinkedinAdsStream:
    @pytest.fixture
    def accounts_stream(self) -> Stream:
        return find_stream("accounts", TEST_CONFIG)

    @pytest.fixture
    def accounts_stream_url(self, accounts_stream) -> str:
        return f"{accounts_stream.retriever.requester.url_base}/{accounts_stream.retriever.requester.path}"

    @pytest.mark.parametrize(
        "response_json, expected",
        (
            ({"elements": []}, None),
            (
                {"elements": [{"data": []}] * 500, "metadata": {"nextPageToken": "next_page_token"}, "paging": {"start": 0, "total": 600}},
                {"next_page_token": "next_page_token"},
            ),
        ),
    )
    def test_next_page_token(self, requests_mock, accounts_stream, accounts_stream_url, response_json, expected):
        """
        Test `_next_page_token` in `SimpleRetriever`.

        After reviewing `SimpleRetriever._next_page_token()`, I realized that `last_page_size`, 
        `last_record`, and `last_page_token_value` are internal state variables that must be 
        manually set or passed. Initially, I tried setting them manually within the state, 
        but the tests still failed with: 
        `TypeError: SimpleRetriever._next_page_token() missing 3 required positional arguments: 
        'last_page_size', 'last_record', and 'last_page_token_value'`.

        To resolve this, I manually set and passed these variables as arguments to 
        `_next_page_token`, which got the tests to pass, as shown here.
        """
        requests_mock.get(accounts_stream_url, json=response_json)
        test_response = requests.get(accounts_stream_url)

        last_page_size = len(response_json.get("elements", []))
        last_record = response_json.get("elements", [])[-1] if response_json.get("elements") else None
        last_page_token_value = None

        result = accounts_stream.retriever._next_page_token(test_response, last_page_size, last_record, last_page_token_value)
        assert expected == result
