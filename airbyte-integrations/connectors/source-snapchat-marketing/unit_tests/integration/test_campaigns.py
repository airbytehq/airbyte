#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.request import HttpRequest

from .config import AD_ACCOUNT_ID, CAMPAIGN_ID, ORGANIZATION_ID, ConfigBuilder
from .request_builder import OAuthRequestBuilder, RequestBuilder
from .response_builder import (
    adaccounts_response,
    campaigns_response,
    error_response,
    oauth_response,
    organizations_response,
)
from .utils import config, read_output


_STREAM_NAME = "campaigns"


def _read(config_builder: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
    return read_output(
        config_builder=config_builder,
        stream_name=_STREAM_NAME,
        sync_mode=SyncMode.full_refresh,
        expecting_exception=expecting_exception,
    )


class TestCampaigns(TestCase):
    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
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

        output = _read(config_builder=config())
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == CAMPAIGN_ID

    @HttpMocker()
    def test_read_records_with_pagination(self, http_mocker: HttpMocker) -> None:
        next_link = f"https://adsapi.snapchat.com/v1/adaccounts/{AD_ACCOUNT_ID}/campaigns?cursor=page2"
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
            campaigns_response(campaign_id="campaign_1", has_next=True, next_link=next_link),
        )
        http_mocker.get(
            HttpRequest(url=next_link),
            campaigns_response(campaign_id="campaign_2", has_next=False),
        )

        output = _read(config_builder=config())
        assert len(output.records) == 2

    @HttpMocker()
    def test_read_records_with_error_403_retry(self, http_mocker: HttpMocker) -> None:
        """Test that 403 errors trigger RETRY behavior as configured in manifest."""
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
        # First request returns 403, then succeeds on retry
        http_mocker.get(
            RequestBuilder.campaigns_endpoint(AD_ACCOUNT_ID).build(),
            [
                error_response(HTTPStatus.FORBIDDEN),
                campaigns_response(campaign_id=CAMPAIGN_ID, ad_account_id=AD_ACCOUNT_ID),
            ],
        )

        output = _read(config_builder=config())
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == CAMPAIGN_ID
