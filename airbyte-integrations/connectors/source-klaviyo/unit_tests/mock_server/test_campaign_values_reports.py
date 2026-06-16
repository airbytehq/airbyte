# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime, timezone
from typing import Any, Dict, List
from unittest import TestCase

import freezegun
import requests_mock as rm
from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from mock_server.config import ConfigBuilder
from mock_server.request_builder import KlaviyoRequestBuilder


_NOW = datetime(2024, 3, 2, 12, 0, 0, tzinfo=timezone.utc)
_STREAM_NAME = "campaign_values_reports"
_API_KEY = "test_api_key_abc123"
_BASE_URL = "https://a.klaviyo.com/api"

_SUPPORTED_METRIC_ID = "supported_metric_ABC123"


def _metrics_response(metric_ids: List[str]) -> HttpResponse:
    """Build a metrics endpoint response with the given metric IDs."""
    return HttpResponse(
        body=json.dumps(
            {
                "data": [
                    {
                        "type": "metric",
                        "id": mid,
                        "attributes": {
                            "name": f"Metric {mid}",
                            "created": "2024-01-01T00:00:00+00:00",
                            "updated": "2024-01-15T00:00:00+00:00",
                            "integration": {"id": "int_001", "name": "API"},
                        },
                    }
                    for mid in metric_ids
                ],
                "links": {"self": f"{_BASE_URL}/metrics", "next": None},
            }
        ),
        status_code=200,
    )


def _campaign_values_success_body() -> Dict[str, Any]:
    """Build a successful campaign-values-reports response body."""
    return {
        "data": {
            "type": "campaign-values-report",
            "attributes": {
                "results": [
                    {
                        "groupings": {
                            "campaign_id": "camp_001",
                            "campaign_message_id": "msg_001",
                            "send_channel": "email",
                        },
                        "statistics": {
                            "opens": 50,
                            "clicks": 25,
                            "delivered": 500,
                            "bounced": 10,
                            "recipients": 510,
                        },
                    }
                ],
            },
        },
        "links": {"self": f"{_BASE_URL}/campaign-values-reports", "next": None},
    }


@freezegun.freeze_time(_NOW.isoformat())
class TestCampaignValuesReportsRateLimiting(TestCase):
    """
    Tests for the campaign_values_reports stream rate limit handling.

    Verifies that the P60D step and max_waiting_time_in_seconds cap work correctly
    to prevent the connector from hanging when Klaviyo's daily rate limit is exhausted.
    """

    @HttpMocker()
    def test_step_p60d_reduces_api_calls(self, http_mocker: HttpMocker):
        """
        Verify that the P60D step reduces the number of API calls.
        With start_date=2024-01-01 and now=2024-03-02, P60D should produce
        2 time windows, not 3 (which P30D would produce).
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 1, 1, tzinfo=timezone.utc)).build()

        http_mocker.get(
            KlaviyoRequestBuilder.metrics_endpoint(_API_KEY).build(),
            _metrics_response([_SUPPORTED_METRIC_ID]),
        )

        call_count = 0

        def counting_callback(request: rm.request._RequestObjectProxy, context: Any) -> str:
            nonlocal call_count
            call_count += 1
            context.status_code = 200
            return json.dumps(_campaign_values_success_body())

        http_mocker._mocker.post(
            f"{_BASE_URL}/campaign-values-reports",
            text=counting_callback,
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.errors) == 0, f"Expected no errors but got: {output.errors}"
        # With P60D step and ~61-day range (Jan 1 to Mar 2), expect exactly 2 calls
        # (Jan 1 - Mar 1, Mar 1 - Mar 2). This confirms P60D is used, not P30D
        # which would produce 3 calls.
        assert call_count == 2, f"Expected 2 API calls with P60D step, got {call_count}"

    @HttpMocker()
    def test_max_backoff_cap_stops_stream_on_daily_rate_limit(self, http_mocker: HttpMocker):
        """
        Verify that when the Retry-After header exceeds max_waiting_time_in_seconds (3600s),
        the stream stops instead of waiting indefinitely. This prevents the connector
        from hanging when Klaviyo's daily rate limit (225/d) is exhausted.
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 1, 1, tzinfo=timezone.utc)).build()

        http_mocker.get(
            KlaviyoRequestBuilder.metrics_endpoint(_API_KEY).build(),
            _metrics_response([_SUPPORTED_METRIC_ID]),
        )

        def rate_limited_callback(request: rm.request._RequestObjectProxy, context: Any) -> str:
            context.status_code = 429
            # Simulate daily rate limit: Retry-After of 8 hours (exceeds 3600s cap)
            context.headers["Retry-After"] = "28800"
            return json.dumps({"errors": [{"status": 429, "detail": "Rate limit exceeded"}]})

        http_mocker._mocker.post(
            f"{_BASE_URL}/campaign-values-reports",
            text=rate_limited_callback,
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        # The stream should error out due to max backoff exceeded rather than hanging
        assert len(output.errors) > 0 or len(output.trace_messages) > 0, (
            "Expected the stream to stop with an error when Retry-After exceeds max_waiting_time_in_seconds"
        )
