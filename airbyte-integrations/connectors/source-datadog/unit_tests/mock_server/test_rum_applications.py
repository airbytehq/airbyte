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
    return DatadogRequestBuilder("v2/rum/applications")


def _application(application_id: str, **attributes: Any) -> dict[str, Any]:
    return {
        "type": "rum_application",
        "id": application_id,
        "attributes": {"application_id": application_id, "name": f"App {application_id}", "type": "browser", **attributes},
    }


class TestRumApplicationsStream(TestCase):
    @HttpMocker()
    def test_reads_every_application_in_one_request(self, http_mocker: HttpMocker) -> None:
        # `GetRUMApplications` takes no paging parameter.
        request = _request().build()
        http_mocker.get(
            request, DatadogPaginatedResponseBuilder("data").with_records([_application("app-1"), _application("app-2")]).build()
        )

        output = read_stream("rum_applications")

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == ["app-1", "app-2"]
        http_mocker.assert_number_of_calls(request, 1)

    @HttpMocker()
    def test_never_emits_a_client_token(self, http_mocker: HttpMocker) -> None:
        # The spec's list item has no client token and its single-application read does, so the stream drops one that comes.
        with_token = _application("app-1", client_token="pub0123456789abcdef", api_key_id=42)
        http_mocker.get(_request().build(), DatadogPaginatedResponseBuilder("data").with_records([with_token]).build())

        output = read_stream("rum_applications")

        assert output.errors == []
        assert [message.record.data for message in output.records] == [_application("app-1", api_key_id=42)]

    def test_declares_no_client_token(self) -> None:
        catalog = get_source().discover(logging.getLogger("airbyte"), CONFIG)

        schema = next(stream.json_schema for stream in catalog.streams if stream.name == "rum_applications")
        assert "client_token" not in schema["properties"]["attributes"]["properties"]

    def test_declares_the_application_id_as_the_primary_key(self) -> None:
        catalog = get_source().discover(logging.getLogger("airbyte"), CONFIG)

        assert next(stream.source_defined_primary_key for stream in catalog.streams if stream.name == "rum_applications") == [["id"]]

    @HttpMocker()
    def test_a_missing_permission_names_rum_apps_read(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_request().build(), datadog_error(403, ["Forbidden", "Failed permission authorization checks"]))

        output = read_stream("rum_applications", expecting_error=True)

        assert [(error.failure_type, error.message) for error in stream_errors(output, "rum_applications")] == [
            (
                FailureType.config_error,
                "The Application Key lacks the rum_apps_read permission: Forbidden, Failed permission authorization checks. "
                "Grant rum_apps_read to the Application Key in Datadog.",
            )
        ]
