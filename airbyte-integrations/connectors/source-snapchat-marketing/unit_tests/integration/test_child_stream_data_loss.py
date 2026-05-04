#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

"""
Regression tests for oncall issue 12134:
Child streams (stats streams) lose data when parent streams have is_client_side_incremental: true.

Root cause: When SubstreamPartitionRouter reads parent records, it creates a fresh parent stream
instance with empty state. The ConcurrentCursor uses config.start_date as the lower bound for
should_be_synced() filtering. Parent records with updated_at < config.start_date are silently
filtered, preventing them from becoming partitions for child streams.

Fix: Remove is_client_side_incremental from parent streams (organizations, adaccounts, ads,
adsquads, campaigns) so their records are never filtered when used by SubstreamPartitionRouter.

These tests verify that campaigns_stats_hourly correctly receives records for ALL campaigns,
even when campaigns have updated_at timestamps before config.start_date.
"""

import json
from typing import List, Optional
from unittest import TestCase

from airbyte_cdk.models import AirbyteStateMessage, SyncMode
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse

from .config import AD_ACCOUNT_ID, ORGANIZATION_ID, ConfigBuilder
from .request_builder import OAuthRequestBuilder, RequestBuilder
from .response_builder import (
    adaccounts_response,
    oauth_response,
    organizations_response,
)
from .utils import config, read_output


_STREAM_NAME = "campaigns_stats_hourly"


def _campaigns_response_with_old_records(campaign_ids: List[str], old_updated_at: str = "2023-06-01T10:00:00.000Z") -> HttpResponse:
    """Create a campaigns response with multiple campaigns that have old updated_at timestamps."""
    campaigns = []
    for cid in campaign_ids:
        campaigns.append({
            "sub_request_status": "SUCCESS",
            "campaign": {
                "id": cid,
                "updated_at": old_updated_at,
                "created_at": "2023-01-01T00:00:00.000Z",
                "name": f"Campaign {cid}",
                "ad_account_id": AD_ACCOUNT_ID,
                "status": "ACTIVE",
                "objective": "AWARENESS",
                "start_time": "2024-01-01T00:00:00.000Z",
                "end_time": "2024-12-31T23:59:59.000Z",
                "daily_budget_micro": 100000000,
                "lifetime_spend_cap_micro": 0,
                "buy_model": "AUCTION",
                "regulations": {},
            },
        })

    body = {
        "request_status": "SUCCESS",
        "request_id": "test_request_id",
        "campaigns": campaigns,
    }
    return HttpResponse(body=json.dumps(body), status_code=200)


def _stats_response(entity_id: str) -> HttpResponse:
    """Create a stats response for a campaign."""
    body = {
        "request_status": "SUCCESS",
        "request_id": "test_request_id",
        "timeseries_stats": [
            {
                "sub_request_status": "SUCCESS",
                "timeseries_stat": {
                    "id": entity_id,
                    "type": "CAMPAIGN",
                    "granularity": "HOUR",
                    "start_time": "2024-01-15T00:00:00.000-0800",
                    "end_time": "2024-01-15T01:00:00.000-0800",
                    "timeseries": [
                        {
                            "start_time": "2024-01-15T00:00:00.000-0800",
                            "end_time": "2024-01-15T01:00:00.000-0800",
                            "stats": {
                                "impressions": 1000,
                                "swipes": 50,
                                "spend": 5000000,
                            },
                        }
                    ],
                },
            }
        ],
    }
    return HttpResponse(body=json.dumps(body), status_code=200)


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


def _setup_parent_chain_mocks(http_mocker: HttpMocker, campaign_ids: List[str], old_updated_at: str = "2023-06-01T10:00:00.000Z") -> None:
    """Set up common mocks for OAuth, organizations, adaccounts, campaigns, and stats."""
    http_mocker.post(OAuthRequestBuilder.oauth_endpoint().build(), oauth_response())
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
        _campaigns_response_with_old_records(campaign_ids, old_updated_at=old_updated_at),
    )
    for cid in campaign_ids:
        http_mocker.get(
            RequestBuilder.campaigns_stats_endpoint(cid).with_any_query_params().build(),
            _stats_response(cid),
        )


class TestChildStreamDataLossRegression(TestCase):
    """Regression tests for oncall issue 12134.

    Verifies that campaigns_stats_hourly sees ALL parent campaigns regardless of their
    updated_at timestamp relative to config.start_date.

    Before the fix: campaigns with updated_at < config.start_date were filtered by
    ConcurrentCursor.should_be_synced() in the SubstreamPartitionRouter path, causing
    child streams to receive 0 records for those campaigns.
    """

    @HttpMocker()
    def test_child_stream_sees_old_parent_records_incremental(self, http_mocker: HttpMocker) -> None:
        """Incremental sync: campaigns_stats_hourly fetches stats for campaigns
        with updated_at before config.start_date (2024-01-01)."""
        campaign_ids = ["campaign_001", "campaign_002", "campaign_003"]
        _setup_parent_chain_mocks(http_mocker, campaign_ids, old_updated_at="2023-06-01T10:00:00.000Z")

        output = _read(config_builder=config(), sync_mode=SyncMode.incremental)

        assert len(output.records) > 0, "Expected stats records but got none"
        record_ids = set(r.record.data.get("id") for r in output.records)
        for cid in campaign_ids:
            assert cid in record_ids, (
                f"Missing stats for campaign {cid}. Got records for: {record_ids}. "
                f"Parent records are being filtered before child stream partition generation."
            )

    @HttpMocker()
    def test_child_stream_sees_old_parent_records_full_refresh(self, http_mocker: HttpMocker) -> None:
        """Full refresh sync: same regression — the ClientSideIncrementalRecordFilterDecorator
        is sync-mode agnostic, so the filtering also occurs in full_refresh mode."""
        campaign_ids = ["campaign_001", "campaign_002", "campaign_003"]
        _setup_parent_chain_mocks(http_mocker, campaign_ids, old_updated_at="2023-06-01T10:00:00.000Z")

        output = _read(config_builder=config(), sync_mode=SyncMode.full_refresh)

        assert len(output.records) > 0, "Expected stats records but got none"
        record_ids = set(r.record.data.get("id") for r in output.records)
        for cid in campaign_ids:
            assert cid in record_ids, (
                f"Missing stats for campaign {cid} in full_refresh. Got records for: {record_ids}."
            )
