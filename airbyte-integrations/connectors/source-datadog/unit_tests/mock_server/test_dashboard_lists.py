# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
from unittest import TestCase

from airbyte_cdk.models import FailureType
from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.conftest import CONFIG, get_source, read_stream, stream_errors
from unit_tests.mock_server.request_builder import DatadogRequestBuilder
from unit_tests.mock_server.response_builder import DatadogPaginatedResponseBuilder, datadog_error


def _request() -> DatadogRequestBuilder:
    return DatadogRequestBuilder("v1/dashboard/lists/manual")


class TestDashboardListsStream(TestCase):
    @HttpMocker()
    def test_reads_every_dashboard_list_in_one_request(self, http_mocker: HttpMocker) -> None:
        # `ListDashboardLists` takes no paging parameter.
        dashboard_lists = [
            {"id": 101, "name": "On-call", "type": "manual_dashboard_list", "dashboard_count": 3},
            {"id": 102, "name": "Billing", "type": "manual_dashboard_list", "dashboard_count": 0},
        ]
        request = _request().build()
        http_mocker.get(request, DatadogPaginatedResponseBuilder("dashboard_lists").with_records(dashboard_lists).build())

        output = read_stream("dashboard_lists")

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == [101, 102]
        http_mocker.assert_number_of_calls(request, 1)

    def test_declares_the_list_id_as_the_primary_key(self) -> None:
        catalog = get_source().discover(logging.getLogger("airbyte"), CONFIG)

        assert next(stream.source_defined_primary_key for stream in catalog.streams if stream.name == "dashboard_lists") == [["id"]]

    @HttpMocker()
    def test_a_missing_permission_names_dashboards_read(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_request().build(), datadog_error(403, ["Forbidden", "Failed permission authorization checks"]))

        output = read_stream("dashboard_lists", expecting_error=True)

        assert [(error.failure_type, error.message) for error in stream_errors(output, "dashboard_lists")] == [
            (
                FailureType.config_error,
                "The Application Key lacks the dashboards_read permission: Forbidden, Failed permission authorization checks. "
                "Grant dashboards_read to the Application Key in Datadog.",
            )
        ]
