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
    return DatadogRequestBuilder("v2/team").with_query_param("page[size]", 100)


def _team(number: int) -> dict[str, Any]:
    return {"type": "team", "id": f"team-{number}", "attributes": {"handle": f"team-{number}", "name": f"Team {number}"}}


class TestTeamsStream(TestCase):
    @HttpMocker()
    def test_reads_two_pages_and_stops_after_the_short_one(self, http_mocker: HttpMocker) -> None:
        full_page = [_team(number) for number in range(100)]
        last_page = [_team(100)]
        second_request = _request().with_query_param("page[number]", 1).build()
        http_mocker.get(_request().build(), DatadogPaginatedResponseBuilder("data").with_records(full_page).build())
        http_mocker.get(second_request, DatadogPaginatedResponseBuilder("data").with_records(last_page).build())

        output = read_stream("teams")

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == [team["id"] for team in full_page + last_page]
        http_mocker.assert_number_of_calls(second_request, 1)

    def test_declares_the_team_id_as_the_primary_key(self) -> None:
        catalog = get_source().discover(logging.getLogger("airbyte"), CONFIG)

        assert next(stream.source_defined_primary_key for stream in catalog.streams if stream.name == "teams") == [["id"]]

    @HttpMocker()
    def test_a_missing_permission_names_teams_read(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_request().build(), datadog_error(403, ["Forbidden", "Failed permission authorization checks"]))

        output = read_stream("teams", expecting_error=True)

        assert [(error.failure_type, error.message) for error in stream_errors(output, "teams")] == [
            (
                FailureType.config_error,
                "The Application Key lacks the teams_read permission: Forbidden, Failed permission authorization checks. "
                "Grant teams_read to the Application Key in Datadog.",
            )
        ]
