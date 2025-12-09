#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from typing import List, Optional
from unittest import TestCase

from airbyte_cdk.models import AirbyteStateMessage, SyncMode
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.request import HttpRequest
from airbyte_cdk.test.state_builder import StateBuilder

from .config import AD_ACCOUNT_ID, ADSQUAD_ID, CAMPAIGN_ID, ORGANIZATION_ID, ConfigBuilder
from .request_builder import OAuthRequestBuilder, RequestBuilder
from .response_builder import (
    adaccounts_response,
    adsquads_response,
    error_response,
    oauth_response,
    organizations_response,
)
from .utils import config, read_output


_STREAM_NAME = "adsquads"


def _read(
    config_builder: ConfigBuilder,
    sync_mode: SyncMode = SyncMode.full_refresh,
    state: Optional[List[AirbyteStateMessage]] = None,
    expecting_exception: bool = False,
) -> EntrypointOutput:
    return read_output(
        config_builder=config_builder,
        stream_name=_STREAM_NAME,
        sync_mode=sync_mode,
        state=state,
        expecting_exception=expecting_exception,
    )


class TestAdsquads(TestCase):
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
            RequestBuilder.adsquads_endpoint(AD_ACCOUNT_ID).build(),
            adsquads_response(adsquad_id=ADSQUAD_ID, ad_account_id=AD_ACCOUNT_ID, campaign_id=CAMPAIGN_ID),
        )

        output = _read(config_builder=config())
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == ADSQUAD_ID

    @HttpMocker()
    def test_read_records_with_pagination(self, http_mocker: HttpMocker) -> None:
        next_link = f"https://adsapi.snapchat.com/v1/adaccounts/{AD_ACCOUNT_ID}/adsquads?cursor=page2"
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
            RequestBuilder.adsquads_endpoint(AD_ACCOUNT_ID).build(),
            adsquads_response(adsquad_id="adsquad_1", has_next=True, next_link=next_link),
        )
        http_mocker.get(
            HttpRequest(url=next_link),
            adsquads_response(adsquad_id="adsquad_2", has_next=False),
        )

        output = _read(config_builder=config())
        assert len(output.records) == 2

    @HttpMocker()
    def test_read_records_with_error_403_retry(self, http_mocker: HttpMocker) -> None:
        """Test that 403 errors trigger RETRY behavior with custom error message from manifest."""
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
            RequestBuilder.adsquads_endpoint(AD_ACCOUNT_ID).build(),
            [
                error_response(HTTPStatus.FORBIDDEN),
                adsquads_response(adsquad_id=ADSQUAD_ID, ad_account_id=AD_ACCOUNT_ID, campaign_id=CAMPAIGN_ID),
            ],
        )

        output = _read(config_builder=config())
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == ADSQUAD_ID

        # Verify custom error message from manifest is logged
        log_messages = [log.log.message for log in output.logs]
        expected_error_prefix = "Got permission error when accessing URL. Skipping"
        assert any(expected_error_prefix in msg for msg in log_messages), (
            f"Expected custom 403 error message '{expected_error_prefix}' in logs"
        )
        assert any(_STREAM_NAME in msg for msg in log_messages), (
            f"Expected stream name '{_STREAM_NAME}' in log messages"
        )


class TestAdsquadsIncremental(TestCase):
    @HttpMocker()
    def test_incremental_sync_with_state(self, http_mocker: HttpMocker) -> None:
        """Test incremental sync with previous state."""
        previous_state_date = "2024-01-15T00:00:00Z"
        state = StateBuilder().with_stream_state(
            _STREAM_NAME,
            {"updated_at": previous_state_date}
        ).build()

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
            RequestBuilder.adsquads_endpoint(AD_ACCOUNT_ID).build(),
            adsquads_response(adsquad_id=ADSQUAD_ID, ad_account_id=AD_ACCOUNT_ID, campaign_id=CAMPAIGN_ID),
        )

        output = _read(config_builder=config(), sync_mode=SyncMode.incremental, state=state)

        assert len(output.records) >= 1, f"Expected at least 1 record, got {len(output.records)}"
        assert output.records[0].record.data["id"] is not None, "Expected record to have id"
        assert len(output.state_messages) > 0, "Expected state messages to be emitted"

        new_state = output.most_recent_state.stream_state.__dict__
        cursor_value = new_state.get("updated_at") or new_state.get("state", {}).get("updated_at")
        assert cursor_value is not None, "Expected cursor value in state"
