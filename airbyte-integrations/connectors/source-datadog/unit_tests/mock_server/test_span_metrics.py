# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
from unittest import TestCase

from airbyte_cdk.models import FailureType
from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.conftest import CONFIG, get_source, read_stream, stream_errors
from unit_tests.mock_server.request_builder import DatadogRequestBuilder
from unit_tests.mock_server.response_builder import DatadogPaginatedResponseBuilder, datadog_error


def _request() -> DatadogRequestBuilder:
    return DatadogRequestBuilder("v2/apm/config/metrics")


class TestSpanMetricsStream(TestCase):
    @HttpMocker()
    def test_reads_every_metric_in_one_request(self, http_mocker: HttpMocker) -> None:
        # `ListSpansMetrics` takes no paging parameter and returns every span-based metric.
        request = _request().build()
        metrics = [
            {"id": "spans.errors", "type": "spans_metrics", "attributes": {"compute": {"aggregation_type": "count"}}},
            {
                "id": "spans.duration",
                "type": "spans_metrics",
                "attributes": {"compute": {"aggregation_type": "distribution", "path": "@duration"}},
            },
        ]
        http_mocker.get(request, DatadogPaginatedResponseBuilder("data").with_records(metrics).build())

        output = read_stream("span_metrics")

        assert output.errors == []
        assert [message.record.data for message in output.records] == metrics
        http_mocker.assert_number_of_calls(request, 1)

    def test_declares_id_as_the_primary_key(self) -> None:
        catalog = get_source().discover(logging.getLogger("airbyte"), CONFIG)

        assert [stream.source_defined_primary_key for stream in catalog.streams if stream.name == "span_metrics"] == [[["id"]]]

    @HttpMocker()
    def test_missing_permission_names_apm_read(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_request().build(), datadog_error(403, ["Forbidden", "Failed permission authorization checks"]))

        output = read_stream("span_metrics", expecting_error=True)

        assert [(error.failure_type, error.message) for error in stream_errors(output, "span_metrics")] == [
            (
                FailureType.config_error,
                "The Application Key lacks the apm_read permission: Forbidden, Failed permission authorization checks. "
                "Grant apm_read to the Application Key in Datadog.",
            )
        ]
