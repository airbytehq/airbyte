# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
from unittest import TestCase

from airbyte_cdk.models import FailureType
from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.conftest import CONFIG, get_source, read_stream, stream_errors
from unit_tests.mock_server.request_builder import DatadogRequestBuilder
from unit_tests.mock_server.response_builder import DatadogPaginatedResponseBuilder, datadog_error


def _request() -> DatadogRequestBuilder:
    return DatadogRequestBuilder("v1/logs/config/indexes")


class TestLogIndexesStream(TestCase):
    @HttpMocker()
    def test_reads_every_index_in_one_request(self, http_mocker: HttpMocker) -> None:
        # `ListLogIndexes` takes no paging parameter and returns every index under `indexes`.
        request = _request().build()
        indexes = [
            {"name": "main", "filter": {"query": "*"}, "num_retention_days": 15, "is_rate_limited": False},
            {"name": "audit", "filter": {"query": "source:audit"}, "num_retention_days": 30, "is_rate_limited": False},
        ]
        http_mocker.get(request, DatadogPaginatedResponseBuilder("indexes").with_records(indexes).build())

        output = read_stream("log_indexes")

        assert output.errors == []
        assert [message.record.data for message in output.records] == indexes
        http_mocker.assert_number_of_calls(request, 1)

    def test_declares_name_as_the_primary_key(self) -> None:
        # A log index has no ID: its name identifies it, as in `GetLogsIndex` (`/api/v1/logs/config/indexes/{name}`).
        catalog = get_source().discover(logging.getLogger("airbyte"), CONFIG)

        assert [stream.source_defined_primary_key for stream in catalog.streams if stream.name == "log_indexes"] == [[["name"]]]

    @HttpMocker()
    def test_missing_permission_names_logs_read_config(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_request().build(), datadog_error(403, ["Forbidden", "Failed permission authorization checks"]))

        output = read_stream("log_indexes", expecting_error=True)

        assert [(error.failure_type, error.message) for error in stream_errors(output, "log_indexes")] == [
            (
                FailureType.config_error,
                "The Application Key lacks the logs_read_config permission: Forbidden, Failed permission authorization checks. "
                "Grant logs_read_config to the Application Key in Datadog.",
            )
        ]
