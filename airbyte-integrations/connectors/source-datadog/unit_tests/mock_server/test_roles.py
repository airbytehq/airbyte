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
    return DatadogRequestBuilder("v2/roles").with_query_param("page[size]", 100)


def _role(number: int) -> dict[str, Any]:
    return {"type": "roles", "id": f"role-{number}", "attributes": {"name": f"Role {number}", "user_count": number}}


class TestRolesStream(TestCase):
    @HttpMocker()
    def test_reads_two_pages_and_stops_after_the_short_one(self, http_mocker: HttpMocker) -> None:
        full_page = [_role(number) for number in range(100)]
        last_page = [_role(100)]
        second_request = _request().with_query_param("page[number]", 1).build()
        http_mocker.get(_request().build(), DatadogPaginatedResponseBuilder("data").with_records(full_page).build())
        http_mocker.get(second_request, DatadogPaginatedResponseBuilder("data").with_records(last_page).build())

        output = read_stream("roles")

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == [role["id"] for role in full_page + last_page]
        http_mocker.assert_number_of_calls(second_request, 1)

    def test_declares_the_role_id_as_the_primary_key(self) -> None:
        catalog = get_source().discover(logging.getLogger("airbyte"), CONFIG)

        assert next(stream.source_defined_primary_key for stream in catalog.streams if stream.name == "roles") == [["id"]]

    @HttpMocker()
    def test_a_missing_permission_names_user_access_read(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_request().build(), datadog_error(403, ["Forbidden", "Failed permission authorization checks"]))

        output = read_stream("roles", expecting_error=True)

        assert [(error.failure_type, error.message) for error in stream_errors(output, "roles")] == [
            (
                FailureType.config_error,
                "The Application Key lacks the user_access_read permission: Forbidden, Failed permission authorization checks. "
                "Grant user_access_read to the Application Key in Datadog.",
            )
        ]
