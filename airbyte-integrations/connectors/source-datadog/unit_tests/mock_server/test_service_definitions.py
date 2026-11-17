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
    return DatadogRequestBuilder("v2/services/definitions").with_query_param("page[size]", 100)


def _definition(number: int) -> dict[str, Any]:
    return {
        "type": "service-definition",
        "id": f"definition-{number}",
        "attributes": {
            "meta": {"ingested-schema-version": "v2.2", "last-modified-time": "2026-11-16T10:00:00Z"},
            "schema": {"schema-version": "v2.2", "dd-service": f"service-{number}", "team": "apis"},
        },
    }


class TestServiceDefinitionsStream(TestCase):
    @HttpMocker()
    def test_reads_two_pages_and_stops_after_the_short_one(self, http_mocker: HttpMocker) -> None:
        full_page = [_definition(number) for number in range(100)]
        last_page = [_definition(100)]
        second_request = _request().with_query_param("page[number]", 1).build()
        http_mocker.get(_request().build(), DatadogPaginatedResponseBuilder("data").with_records(full_page).build())
        http_mocker.get(second_request, DatadogPaginatedResponseBuilder("data").with_records(last_page).build())

        output = read_stream("service_definitions")

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == [record["id"] for record in full_page + last_page]
        http_mocker.assert_number_of_calls(second_request, 1)

    @HttpMocker()
    def test_keeps_the_hyphenated_keys_as_datadog_sends_them(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_request().build(), DatadogPaginatedResponseBuilder("data").with_records([_definition(1)]).build())

        output = read_stream("service_definitions")

        assert output.errors == []
        assert [message.record.data for message in output.records] == [_definition(1)]

    def test_declares_the_definition_id_as_the_primary_key(self) -> None:
        catalog = get_source().discover(logging.getLogger("airbyte"), CONFIG)

        assert next(stream.source_defined_primary_key for stream in catalog.streams if stream.name == "service_definitions") == [["id"]]

    @HttpMocker()
    def test_a_missing_permission_names_apm_service_catalog_read(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_request().build(), datadog_error(403, ["Forbidden", "Failed permission authorization checks"]))

        output = read_stream("service_definitions", expecting_error=True)

        assert [(error.failure_type, error.message) for error in stream_errors(output, "service_definitions")] == [
            (
                FailureType.config_error,
                "The Application Key lacks the apm_service_catalog_read permission: Forbidden, Failed permission authorization "
                "checks. Grant apm_service_catalog_read to the Application Key in Datadog.",
            )
        ]
