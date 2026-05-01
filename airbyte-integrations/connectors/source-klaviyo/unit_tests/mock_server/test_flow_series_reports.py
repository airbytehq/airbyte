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


_NOW = datetime(2024, 2, 1, 12, 0, 0, tzinfo=timezone.utc)
_STREAM_NAME = "flow_series_reports"
_API_KEY = "test_api_key_abc123"
_BASE_URL = "https://a.klaviyo.com/api"

_UNSUPPORTED_METRIC_ID = "unsupported_metric_RJYhz9"
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


def _flow_series_success_body() -> Dict[str, Any]:
    """Build a successful flow-series-reports response body."""
    return {
        "data": {
            "type": "flow-series-report",
            "attributes": {
                "results": [
                    {
                        "groupings": {
                            "flow_id": "flow_001",
                            "flow_message_id": "msg_001",
                            "send_channel": "email",
                        },
                        "statistics": {
                            "opens": 10,
                            "clicks": 5,
                            "delivered": 100,
                            "bounced": 2,
                            "recipients": 102,
                        },
                    }
                ],
            },
        },
        "links": {"self": f"{_BASE_URL}/flow-series-reports", "next": None},
    }


def _unsupported_metric_error_body() -> Dict[str, Any]:
    """Build the Klaviyo 400 error body for unsupported conversion metrics."""
    return {
        "errors": [
            {
                "id": "error-id",
                "status": 400,
                "code": "invalid",
                "title": "Bad request",
                "detail": "Passed in conversion metric does not support querying for values data",
            }
        ]
    }


@freezegun.freeze_time(_NOW.isoformat())
class TestFlowSeriesReportsUnsupportedMetric(TestCase):
    """
    Tests for the flow_series_reports stream handling of HTTP 400 errors
    from unsupported conversion metrics.

    The Klaviyo API returns HTTP 400 with "does not support querying for
    values data" for certain conversion metrics. The connector should
    skip these partitions and continue syncing other metrics.
    """

    @HttpMocker()
    def test_ignores_400_unsupported_conversion_metric(self, http_mocker: HttpMocker):
        """
        Verify that when one metric returns the unsupported 400 error,
        the sync continues and returns records from other supported metrics.
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 1, 1, tzinfo=timezone.utc)).build()

        # Mock the parent metrics_for_reporting stream (GET /metrics)
        http_mocker.get(
            KlaviyoRequestBuilder.metrics_endpoint(_API_KEY).build(),
            _metrics_response([_SUPPORTED_METRIC_ID, _UNSUPPORTED_METRIC_ID]),
        )

        # Use the underlying requests_mock to handle POST with dynamic body matching
        def flow_series_callback(request: rm.request._RequestObjectProxy, context: Any) -> str:
            body = json.loads(request.body)
            metric_id = body.get("data", {}).get("attributes", {}).get("conversion_metric_id", "")
            if metric_id == _UNSUPPORTED_METRIC_ID:
                context.status_code = 400
                return json.dumps(_unsupported_metric_error_body())
            context.status_code = 200
            return json.dumps(_flow_series_success_body())

        http_mocker._mocker.post(
            f"{_BASE_URL}/flow-series-reports",
            text=flow_series_callback,
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        # The sync should complete without errors
        assert len(output.errors) == 0, f"Expected no errors but got: {output.errors}"
        # We should have records from the supported metric
        assert len(output.records) >= 1

    @HttpMocker()
    def test_all_metrics_unsupported_yields_zero_records(self, http_mocker: HttpMocker):
        """
        Verify that when all metrics are unsupported, the sync completes
        with zero records and no errors.
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 1, 1, tzinfo=timezone.utc)).build()

        # Mock the parent metrics_for_reporting stream (GET /metrics)
        http_mocker.get(
            KlaviyoRequestBuilder.metrics_endpoint(_API_KEY).build(),
            _metrics_response([_UNSUPPORTED_METRIC_ID]),
        )

        # Every POST returns 400 unsupported
        def all_unsupported_callback(request: rm.request._RequestObjectProxy, context: Any) -> str:
            context.status_code = 400
            return json.dumps(_unsupported_metric_error_body())

        http_mocker._mocker.post(
            f"{_BASE_URL}/flow-series-reports",
            text=all_unsupported_callback,
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.errors) == 0, f"Expected no errors but got: {output.errors}"
        assert len(output.records) == 0
