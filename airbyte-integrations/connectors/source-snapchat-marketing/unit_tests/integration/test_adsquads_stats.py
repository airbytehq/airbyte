#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from typing import List, Optional
from unittest import TestCase

from airbyte_cdk.models import AirbyteStateMessage, SyncMode
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder

from .config import AD_ACCOUNT_ID, ADSQUAD_ID, CAMPAIGN_ID, ORGANIZATION_ID, ConfigBuilder
from .request_builder import OAuthRequestBuilder, RequestBuilder
from .response_builder import (
    adaccounts_response,
    adsquads_response,
    error_response,
    oauth_response,
    organizations_response,
    stats_lifetime_response,
    stats_timeseries_response,
)
from .utils import config, read_output


def _read(
    config_builder: ConfigBuilder,
    stream_name: str,
    sync_mode: SyncMode = SyncMode.full_refresh,
    state: Optional[List[AirbyteStateMessage]] = None,
    expecting_exception: bool = False,
) -> EntrypointOutput:
    return read_output(
        config_builder=config_builder,
        stream_name=stream_name,
        sync_mode=sync_mode,
        state=state,
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
        RequestBuilder.adsquads_endpoint(AD_ACCOUNT_ID).build(),
        adsquads_response(adsquad_id=ADSQUAD_ID, ad_account_id=AD_ACCOUNT_ID, campaign_id=CAMPAIGN_ID),
    )


class TestAdsquadsStatsHourly(TestCase):
    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        _setup_parent_mocks(http_mocker)
        http_mocker.get(
            RequestBuilder.adsquads_stats_endpoint(ADSQUAD_ID).with_any_query_params().build(),
            stats_timeseries_response(entity_id=ADSQUAD_ID, granularity="HOUR"),
        )

        output = _read(config_builder=config(), stream_name="adsquads_stats_hourly")
        assert len(output.records) >= 1

    @HttpMocker()
    def test_read_records_with_error_403_retry(self, http_mocker: HttpMocker) -> None:
        """Test that 403 errors trigger RETRY behavior with custom error message from manifest."""
        _setup_parent_mocks(http_mocker)
        # First request returns 403, then succeeds on retry
        http_mocker.get(
            RequestBuilder.adsquads_stats_endpoint(ADSQUAD_ID).with_any_query_params().build(),
            [
                error_response(HTTPStatus.FORBIDDEN),
                stats_timeseries_response(entity_id=ADSQUAD_ID, granularity="HOUR"),
            ],
        )

        output = _read(config_builder=config(), stream_name="adsquads_stats_hourly")
        assert len(output.records) >= 1

        # Verify custom error message from manifest is logged
        log_messages = [log.log.message for log in output.logs]
        expected_error_prefix = "Got permission error when accessing URL. Skipping"
        assert any(expected_error_prefix in msg for msg in log_messages), (
            f"Expected custom 403 error message '{expected_error_prefix}' in logs"
        )


class TestAdsquadsStatsDaily(TestCase):
    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        _setup_parent_mocks(http_mocker)
        http_mocker.get(
            RequestBuilder.adsquads_stats_endpoint(ADSQUAD_ID).with_any_query_params().build(),
            stats_timeseries_response(entity_id=ADSQUAD_ID, granularity="DAY"),
        )

        output = _read(config_builder=config(), stream_name="adsquads_stats_daily")
        assert len(output.records) == 1


class TestAdsquadsStatsLifetime(TestCase):
    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        _setup_parent_mocks(http_mocker)
        http_mocker.get(
            RequestBuilder.adsquads_stats_endpoint(ADSQUAD_ID).with_any_query_params().build(),
            stats_lifetime_response(entity_id=ADSQUAD_ID),
        )

        output = _read(config_builder=config(), stream_name="adsquads_stats_lifetime")
        assert len(output.records) == 1


class TestAdsquadsStatsIncremental(TestCase):
    @HttpMocker()
    def test_incremental_sync_with_state(self, http_mocker: HttpMocker) -> None:
        """Test incremental sync with previous state for stats streams."""
        previous_state_date = "2024-01-15T00:00:00Z"
        state = StateBuilder().with_stream_state(
            "adsquads_stats_hourly",
            {"start_time": previous_state_date}
        ).build()

        _setup_parent_mocks(http_mocker)
        http_mocker.get(
            RequestBuilder.adsquads_stats_endpoint(ADSQUAD_ID).with_any_query_params().build(),
            stats_timeseries_response(entity_id=ADSQUAD_ID, granularity="HOUR"),
        )

        output = _read(config_builder=config(), stream_name="adsquads_stats_hourly", sync_mode=SyncMode.incremental, state=state)

        assert len(output.records) >= 1, f"Expected at least 1 record, got {len(output.records)}"
        assert len(output.state_messages) > 0, "Expected state messages to be emitted"

        new_state = output.most_recent_state.stream_state.__dict__
        cursor_value = new_state.get("start_time") or new_state.get("state", {}).get("start_time")
        assert cursor_value is not None, "Expected cursor value in state"
