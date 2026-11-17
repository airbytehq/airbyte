# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
from typing import Any
from unittest import TestCase

from airbyte_cdk.models import FailureType
from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.conftest import CONFIG, get_source, read_stream, stream_errors
from unit_tests.mock_server.request_builder import DatadogRequestBuilder
from unit_tests.mock_server.response_builder import DatadogPaginatedResponseBuilder, datadog_error


def _request() -> DatadogRequestBuilder:
    return DatadogRequestBuilder("v1/slo/correction").with_query_param("limit", 25)


def _correction(number: int) -> dict[str, Any]:
    return {
        "type": "correction",
        "id": f"correction-{number}",
        "attributes": {"category": "Scheduled Maintenance", "slo_id": "slo-1", "start": 1763251200, "end": 1763254800},
    }


class TestSloCorrectionsStream(TestCase):
    @HttpMocker()
    def test_reads_two_pages_and_stops_after_the_short_one(self, http_mocker: HttpMocker) -> None:
        full_page = [_correction(number) for number in range(25)]
        last_page = [_correction(25)]
        second_request = _request().with_query_param("offset", 25).build()
        http_mocker.get(
            _request().build(),
            DatadogPaginatedResponseBuilder("data").with_records(full_page).with_meta({"page": {"total_count": 26}}).build(),
        )
        http_mocker.get(
            second_request,
            DatadogPaginatedResponseBuilder("data").with_records(last_page).with_meta({"page": {"total_count": 26}}).build(),
        )

        output = read_stream("slo_corrections")

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == [record["id"] for record in full_page + last_page]
        http_mocker.assert_number_of_calls(second_request, 1)

    def test_declares_the_correction_id_as_the_primary_key(self) -> None:
        catalog = get_source().discover(logging.getLogger("airbyte"), CONFIG)

        assert next(stream.source_defined_primary_key for stream in catalog.streams if stream.name == "slo_corrections") == [["id"]]

    @HttpMocker()
    def test_a_missing_permission_names_slos_read(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_request().build(), datadog_error(403, ["Forbidden", "Failed permission authorization checks"]))

        output = read_stream("slo_corrections", expecting_error=True)

        assert [(error.failure_type, error.message) for error in stream_errors(output, "slo_corrections")] == [
            (
                FailureType.config_error,
                "The Application Key lacks the slos_read permission: Forbidden, Failed permission authorization checks. "
                "Grant slos_read to the Application Key in Datadog.",
            )
        ]
