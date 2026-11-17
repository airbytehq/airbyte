# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
from unittest import TestCase

from airbyte_cdk.models import FailureType
from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.conftest import CONFIG, get_source, read_stream, stream_errors
from unit_tests.mock_server.request_builder import DatadogRequestBuilder
from unit_tests.mock_server.response_builder import DatadogPaginatedResponseBuilder, datadog_error


def _request() -> DatadogRequestBuilder:
    return DatadogRequestBuilder("v2/permissions")


class TestPermissionsStream(TestCase):
    @HttpMocker()
    def test_reads_every_permission_in_one_request(self, http_mocker: HttpMocker) -> None:
        # `ListPermissions` takes no paging parameter.
        permissions = [
            {"type": "permissions", "id": "permission-1", "attributes": {"name": "dashboards_read", "group_name": "Dashboards"}},
            {"type": "permissions", "id": "permission-2", "attributes": {"name": "teams_read", "group_name": "Teams"}},
        ]
        request = _request().build()
        http_mocker.get(request, DatadogPaginatedResponseBuilder("data").with_records(permissions).build())

        output = read_stream("permissions")

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == ["permission-1", "permission-2"]
        http_mocker.assert_number_of_calls(request, 1)

    def test_declares_the_permission_id_as_the_primary_key(self) -> None:
        catalog = get_source().discover(logging.getLogger("airbyte"), CONFIG)

        assert next(stream.source_defined_primary_key for stream in catalog.streams if stream.name == "permissions") == [["id"]]

    @HttpMocker()
    def test_a_missing_permission_names_user_access_read(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_request().build(), datadog_error(403, ["Forbidden", "Failed permission authorization checks"]))

        output = read_stream("permissions", expecting_error=True)

        assert [(error.failure_type, error.message) for error in stream_errors(output, "permissions")] == [
            (
                FailureType.config_error,
                "The Application Key lacks the user_access_read permission: Forbidden, Failed permission authorization checks. "
                "Grant user_access_read to the Application Key in Datadog.",
            )
        ]
