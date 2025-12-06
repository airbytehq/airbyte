#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker

from .config import AD_ACCOUNT_ID, CAMPAIGN_ID, ORGANIZATION_ID, ConfigBuilder
from .request_builder import OAuthRequestBuilder, RequestBuilder
from .response_builder import (
    adaccounts_response,
    campaigns_response,
    error_response,
    oauth_response,
    organizations_response,
    stats_lifetime_response,
    stats_timeseries_response,
)
from .utils import config, read_output


def _read(config_builder: ConfigBuilder, stream_name: str, expecting_exception: bool = False) -> EntrypointOutput:
    return read_output(
        config_builder=config_builder,
        stream_name=stream_name,
        sync_mode=SyncMode.full_refresh,
        expecting_exception=expecting_exception,
    )


def _setup_parent_mocks(http_mocker: HttpMocker) -> None:
    http_mocker.post(
        OAuthRequestBuilder.oauth_endpoint().build(),
        oauth_response(),
    )
    http_mocker.get(
        RequestBuilder.organizations_endpoint("me").build(),
        organizations_response(organization_id=ORGANIZATION_ID),
    )
    http_mocker.get(
        RequestBuilder.adaccounts_endpoint(ORGANIZATION_ID).build(),
        adaccounts_response(ad_account_id=AD_ACCOUNT_ID, organization_id=ORGANIZATION_ID),
    )
    http_mocker.get(
        RequestBuilder.campaigns_endpoint(AD_ACCOUNT_ID).build(),
        campaigns_response(campaign_id=CAMPAIGN_ID, ad_account_id=AD_ACCOUNT_ID),
    )


class TestCampaignsStatsHourly(TestCase):
    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        _setup_parent_mocks(http_mocker)
        http_mocker.get(
            RequestBuilder.campaigns_stats_endpoint(CAMPAIGN_ID).with_any_query_params().build(),
            stats_timeseries_response(entity_id=CAMPAIGN_ID, granularity="HOUR"),
        )

        output = _read(config_builder=config(), stream_name="campaigns_stats_hourly")
        assert len(output.records) >= 1

    @HttpMocker()
    def test_read_records_with_error_401(self, http_mocker: HttpMocker) -> None:
        _setup_parent_mocks(http_mocker)
        http_mocker.get(
            RequestBuilder.campaigns_stats_endpoint(CAMPAIGN_ID).with_any_query_params().build(),
            error_response(HTTPStatus.UNAUTHORIZED),
        )

        output = _read(config_builder=config(), stream_name="campaigns_stats_hourly", expecting_exception=True)
        assert len(output.records) == 0


class TestCampaignsStatsDaily(TestCase):
    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        _setup_parent_mocks(http_mocker)
        http_mocker.get(
            RequestBuilder.campaigns_stats_endpoint(CAMPAIGN_ID).with_any_query_params().build(),
            stats_timeseries_response(entity_id=CAMPAIGN_ID, granularity="DAY"),
        )

        output = _read(config_builder=config(), stream_name="campaigns_stats_daily")
        assert len(output.records) == 1


class TestCampaignsStatsLifetime(TestCase):
    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        _setup_parent_mocks(http_mocker)
        http_mocker.get(
            RequestBuilder.campaigns_stats_endpoint(CAMPAIGN_ID).with_any_query_params().build(),
            stats_lifetime_response(entity_id=CAMPAIGN_ID),
        )

        output = _read(config_builder=config(), stream_name="campaigns_stats_lifetime")
        assert len(output.records) == 1
