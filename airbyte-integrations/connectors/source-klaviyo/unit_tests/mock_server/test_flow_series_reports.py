# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime, timezone
from unittest import TestCase

import freezegun
from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from mock_server.config import ConfigBuilder
from mock_server.request_builder import KlaviyoRequestBuilder
from mock_server.response_builder import KlaviyoPaginatedResponseBuilder


_NOW = datetime(2024, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
_STREAM_NAME = "flow_series_reports"
_API_KEY = "test_api_key_abc123"

_FLOW_SERIES_STATISTICS = [
    "opens",
    "opens_unique",
    "clicks",
    "clicks_unique",
    "delivered",
    "bounced",
    "bounced_or_failed",
    "bounced_or_failed_rate",
    "failed",
    "failed_rate",
    "conversions",
    "conversion_value",
    "conversion_rate",
    "conversion_uniques",
    "click_rate",
    "open_rate",
    "click_to_open_rate",
    "delivery_rate",
    "bounce_rate",
    "recipients",
    "revenue_per_recipient",
    "average_order_value",
]


def _build_report_request_body(report_type, metric_id, start_time, end_time, statistics):
    return {
        "data": {
            "type": report_type,
            "attributes": {
                "statistics": statistics,
                "timeframe": {
                    "start": start_time,
                    "end": end_time,
                },
                "interval": "daily",
                "conversion_metric_id": metric_id,
            },
        }
    }


def _build_klaviyo_400_error_response(detail):
    return HttpResponse(
        body=json.dumps(
            {
                "errors": [
                    {
                        "id": "error-id",
                        "status": 400,
                        "code": "invalid",
                        "title": "Bad Request",
                        "detail": detail,
                    }
                ]
            }
        ),
        status_code=400,
    )


@freezegun.freeze_time(_NOW.isoformat())
class TestFlowSeriesReportsIgnoresUnsupportedMetrics(TestCase):
    """
    Tests that the flow_series_reports stream gracefully handles HTTP 400 errors
    from Klaviyo when a conversion metric does not support values data queries.

    Some metrics (e.g. custom conversion metrics) are returned by the parent
    metrics stream but cause the reporting API to return HTTP 400 with
    "Passed in conversion metric does not support querying for values data".
    The connector should skip these partitions and continue syncing.
    """

    @HttpMocker()
    def test_ignores_400_unsupported_conversion_metric(self, http_mocker: HttpMocker):
        """
        Given: Two metrics from the parent stream, one of which does not support values data queries
        When: The connector syncs the flow_series_reports stream
        Then: The unsupported metric partition is skipped (HTTP 400 IGNORED) and
              the supported metric's records are returned without error
        """
        start_time = "2024-05-02T12:00:00+0000"
        end_time = "2024-06-01T12:00:00+0000"

        config = (
            ConfigBuilder()
            .with_api_key(_API_KEY)
            .with_start_date(datetime(2024, 5, 2, 12, 0, 0, tzinfo=timezone.utc))
            .build()
        )

        # Mock parent metrics stream returning two metrics
        http_mocker.get(
            KlaviyoRequestBuilder.metrics_endpoint(_API_KEY).with_any_query_params().build(),
            KlaviyoPaginatedResponseBuilder.single_page(
                [
                    {
                        "type": "metric",
                        "id": "supported_metric",
                        "attributes": {"name": "Placed Order", "created": "2024-01-01T00:00:00+00:00", "updated": "2024-01-01T00:00:00+00:00", "integration": {}},
                    },
                    {
                        "type": "metric",
                        "id": "unsupported_metric",
                        "attributes": {"name": "Custom Conversion", "created": "2024-01-01T00:00:00+00:00", "updated": "2024-01-01T00:00:00+00:00", "integration": {}},
                    },
                ]
            ),
        )

        # Mock POST for the supported metric: returns valid report data
        supported_body = _build_report_request_body("flow-series-report", "supported_metric", start_time, end_time, _FLOW_SERIES_STATISTICS)
        http_mocker.post(
            HttpRequest(
                url="https://a.klaviyo.com/api/flow-series-reports",
                body=supported_body,
            ),
            HttpResponse(
                body=json.dumps(
                    {
                        "data": {
                            "type": "flow-series-report",
                            "attributes": {
                                "results": [
                                    {
                                        "groupings": {"flow_id": "flow_abc", "flow_message_id": "msg_001", "send_channel": "email"},
                                        "statistics": {"opens": 10, "clicks": 5},
                                    }
                                ],
                            },
                        },
                        "links": {"self": "https://a.klaviyo.com/api/flow-series-reports", "next": None},
                    }
                ),
                status_code=200,
            ),
        )

        # Mock POST for the unsupported metric: returns HTTP 400
        unsupported_body = _build_report_request_body("flow-series-report", "unsupported_metric", start_time, end_time, _FLOW_SERIES_STATISTICS)
        http_mocker.post(
            HttpRequest(
                url="https://a.klaviyo.com/api/flow-series-reports",
                body=unsupported_body,
            ),
            _build_klaviyo_400_error_response("Passed in conversion metric does not support querying for values data"),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        # The sync should NOT fail — the unsupported metric is silently skipped
        assert len(output.errors) == 0, f"Expected no errors but got: {output.errors}"

        # Only records from the supported metric should be present
        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["flow_id"] == "flow_abc"
        assert record["conversion_metric_id"] == "supported_metric"

    @HttpMocker()
    def test_all_metrics_unsupported_yields_zero_records(self, http_mocker: HttpMocker):
        """
        Given: All metrics from the parent stream return the unsupported 400 error
        When: The connector syncs the flow_series_reports stream
        Then: The sync completes with zero records and no errors (all partitions ignored)
        """
        start_time = "2024-05-02T12:00:00+0000"
        end_time = "2024-06-01T12:00:00+0000"

        config = (
            ConfigBuilder()
            .with_api_key(_API_KEY)
            .with_start_date(datetime(2024, 5, 2, 12, 0, 0, tzinfo=timezone.utc))
            .build()
        )

        # Mock parent metrics stream returning one metric
        http_mocker.get(
            KlaviyoRequestBuilder.metrics_endpoint(_API_KEY).with_any_query_params().build(),
            KlaviyoPaginatedResponseBuilder.single_page(
                [
                    {
                        "type": "metric",
                        "id": "unsupported_only",
                        "attributes": {"name": "Custom Conversion", "created": "2024-01-01T00:00:00+00:00", "updated": "2024-01-01T00:00:00+00:00", "integration": {}},
                    },
                ]
            ),
        )

        # Mock POST returning the specific unsupported metric 400 error
        body = _build_report_request_body("flow-series-report", "unsupported_only", start_time, end_time, _FLOW_SERIES_STATISTICS)
        http_mocker.post(
            HttpRequest(
                url="https://a.klaviyo.com/api/flow-series-reports",
                body=body,
            ),
            _build_klaviyo_400_error_response("Passed in conversion metric does not support querying for values data"),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        # All partitions ignored: zero records, no errors
        assert len(output.errors) == 0, f"Expected no errors but got: {output.errors}"
        assert len(output.records) == 0
