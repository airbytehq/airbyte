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

from .config import AD_ACCOUNT_ID, CAMPAIGN_ID, ORGANIZATION_ID, ConfigBuilder
from .request_builder import OAuthRequestBuilder, RequestBuilder
from .response_builder import (
    adaccounts_response,
    campaigns_response,
    create_multiple_records_response,
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
        RequestBuilder.campaigns_endpoint(AD_ACCOUNT_ID).build(),
        campaigns_response(campaign_id=CAMPAIGN_ID, ad_account_id=AD_ACCOUNT_ID),
    )


def _setup_parent_mocks_multiple_campaigns(http_mocker: HttpMocker, campaign_ids: List[str]) -> None:
    """Setup parent mocks with multiple campaigns for testing substreams."""
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
        create_multiple_records_response("campaigns", campaign_ids),
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

        # Enhanced assertions
        assert len(output.records) == 5  # 5 weekly time slices (Jan 1-31 with step: P1W)
        record = output.records[0].record.data
        assert record.get("id") == CAMPAIGN_ID, f"Expected id={CAMPAIGN_ID}, got {record.get('id')}"

    @HttpMocker()
    def test_read_records_with_error_403_retry(self, http_mocker: HttpMocker) -> None:
        """Test that 403 errors trigger RETRY behavior with custom error message from manifest."""
        _setup_parent_mocks(http_mocker)
        # First request returns 403, then succeeds on retry
        http_mocker.get(
            RequestBuilder.campaigns_stats_endpoint(CAMPAIGN_ID).with_any_query_params().build(),
            [
                error_response(HTTPStatus.FORBIDDEN),
                stats_timeseries_response(entity_id=CAMPAIGN_ID, granularity="HOUR"),
            ],
        )

        output = _read(config_builder=config(), stream_name="campaigns_stats_hourly")
        assert len(output.records) == 5  # 5 weekly time slices

        # Verify custom error message from manifest is logged
        log_messages = [log.log.message for log in output.logs]
        expected_error_prefix = "Got permission error when accessing URL. Skipping"
        assert any(
            expected_error_prefix in msg for msg in log_messages
        ), f"Expected custom 403 error message '{expected_error_prefix}' in logs"


class TestCampaignsStatsDaily(TestCase):
    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        _setup_parent_mocks(http_mocker)
        http_mocker.get(
            RequestBuilder.campaigns_stats_endpoint(CAMPAIGN_ID).with_any_query_params().build(),
            stats_timeseries_response(entity_id=CAMPAIGN_ID, granularity="DAY"),
        )

        output = _read(config_builder=config(), stream_name="campaigns_stats_daily")

        assert len(output.records) == 1  # Daily: step P1M = 1 monthly slice
        record = output.records[0].record.data
        assert record.get("id") == CAMPAIGN_ID, f"Expected id={CAMPAIGN_ID}, got {record.get('id')}"


class TestCampaignsStatsLifetime(TestCase):
    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        _setup_parent_mocks(http_mocker)
        http_mocker.get(
            RequestBuilder.campaigns_stats_endpoint(CAMPAIGN_ID).with_any_query_params().build(),
            stats_lifetime_response(entity_id=CAMPAIGN_ID),
        )

        output = _read(config_builder=config(), stream_name="campaigns_stats_lifetime")

        assert len(output.records) == 1  # Lifetime: no step
        record = output.records[0].record.data
        assert record.get("id") == CAMPAIGN_ID, f"Expected id={CAMPAIGN_ID}, got {record.get('id')}"


class TestCampaignsStatsTransformations(TestCase):
    @HttpMocker()
    def test_transformations_add_fields(self, http_mocker: HttpMocker) -> None:
        """Test that AddFields transformations are applied correctly.

        The manifest defines these transformations for campaigns_stats_hourly:
        - AddFields: id (from stream_slice['id'])
        - AddFields: type = CAMPAIGN
        - AddFields: granularity = HOUR
        - AddFields: spend (from record.get('stats', {}).get('spend'))
        - RemoveFields: stats
        """
        _setup_parent_mocks(http_mocker)
        http_mocker.get(
            RequestBuilder.campaigns_stats_endpoint(CAMPAIGN_ID).with_any_query_params().build(),
            stats_timeseries_response(entity_id=CAMPAIGN_ID, granularity="HOUR"),
        )

        output = _read(config_builder=config(), stream_name="campaigns_stats_hourly")
        assert len(output.records) == 5  # 5 weekly time slices

        record = output.records[0].record.data
        # Verify AddFields transformations
        assert record.get("id") == CAMPAIGN_ID
        assert record.get("type") == "CAMPAIGN"
        assert record.get("granularity") == "HOUR"
        # Verify spend field is extracted from stats
        assert "spend" in record
        # Verify RemoveFields transformation - stats should be removed
        assert "stats" not in record


class TestCampaignsStatsSubstreamMultipleParents(TestCase):
    @HttpMocker()
    def test_substream_with_two_parent_records(self, http_mocker: HttpMocker) -> None:
        """Test that substream correctly processes multiple parent records.

        The campaigns_stats streams use SubstreamPartitionRouter with campaigns as parent.
        This test verifies that stats are fetched for each parent campaign.
        """
        campaign_1 = "campaign_001"
        campaign_2 = "campaign_002"

        _setup_parent_mocks_multiple_campaigns(http_mocker, [campaign_1, campaign_2])

        # Mock stats endpoint for each parent campaign
        http_mocker.get(
            RequestBuilder.campaigns_stats_endpoint(campaign_1).with_any_query_params().build(),
            stats_timeseries_response(entity_id=campaign_1, granularity="HOUR"),
        )
        http_mocker.get(
            RequestBuilder.campaigns_stats_endpoint(campaign_2).with_any_query_params().build(),
            stats_timeseries_response(entity_id=campaign_2, granularity="HOUR"),
        )

        output = _read(config_builder=config(), stream_name="campaigns_stats_hourly")

        # Verify records from both parent campaigns are returned
        assert len(output.records) == 10  # 2 parents × 5 weekly time slices = 10 records
        record_ids = [r.record.data.get("id") for r in output.records]
        assert campaign_1 in record_ids
        assert campaign_2 in record_ids


class TestCampaignsStatsIncremental(TestCase):
    @HttpMocker()
    def test_incremental_first_sync_emits_state(self, http_mocker: HttpMocker) -> None:
        """Test that first sync (no state) emits state message with cursor value."""
        _setup_parent_mocks(http_mocker)
        http_mocker.get(
            RequestBuilder.campaigns_stats_endpoint(CAMPAIGN_ID).with_any_query_params().build(),
            stats_timeseries_response(entity_id=CAMPAIGN_ID, granularity="HOUR"),
        )

        output = _read(config_builder=config(), stream_name="campaigns_stats_hourly", sync_mode=SyncMode.incremental)

        assert len(output.state_messages) > 0, "Expected state messages to be emitted"
        assert len(output.records) == 5  # 5 weekly time slices

        # Get latest record's cursor
        latest_record = output.records[-1].record.data
        record_cursor_value = latest_record.get("start_time")

        # Get state cursor
        new_state = output.most_recent_state.stream_state.__dict__
        state_cursor_value = new_state.get("start_time") or new_state.get("state", {}).get("start_time")

        # Validate state matches record
        assert state_cursor_value is not None, "Expected 'start_time' in state"
        assert record_cursor_value is not None, "Expected 'start_time' in record"
        assert state_cursor_value == record_cursor_value or state_cursor_value.startswith(
            record_cursor_value[:10]
        ), f"Expected state to match latest record. State: {state_cursor_value}, Record: {record_cursor_value}"

    @HttpMocker()
    def test_incremental_sync_with_state(self, http_mocker: HttpMocker) -> None:
        """Test incremental sync with previous state for stats streams."""
        previous_state_date = "2024-01-15T00:00:00.000000Z"
        state = StateBuilder().with_stream_state("campaigns_stats_hourly", {"start_time": previous_state_date}).build()

        _setup_parent_mocks(http_mocker)
        http_mocker.get(
            RequestBuilder.campaigns_stats_endpoint(CAMPAIGN_ID).with_any_query_params().build(),
            stats_timeseries_response(entity_id=CAMPAIGN_ID, granularity="HOUR"),
        )

        output = _read(config_builder=config(), stream_name="campaigns_stats_hourly", sync_mode=SyncMode.incremental, state=state)

        assert len(output.state_messages) > 0, "Expected state messages to be emitted"
        assert len(output.records) == 3  # 3 remaining weekly time slices after state date (Jan 15-31)

        # Get latest record's cursor
        latest_record = output.records[-1].record.data
        record_cursor_value = latest_record.get("start_time")

        # Get state cursor
        new_state = output.most_recent_state.stream_state.__dict__
        state_cursor_value = new_state.get("start_time") or new_state.get("state", {}).get("start_time")

        # Validate state matches record
        assert state_cursor_value is not None, "Expected 'start_time' in state"
        assert record_cursor_value is not None, "Expected 'start_time' in record"
        assert state_cursor_value == record_cursor_value or state_cursor_value.startswith(
            record_cursor_value[:10]
        ), f"Expected state to match latest record. State: {state_cursor_value}, Record: {record_cursor_value}"
