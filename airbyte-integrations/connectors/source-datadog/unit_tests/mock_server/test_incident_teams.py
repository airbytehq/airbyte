# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from unittest import TestCase

from airbyte_cdk.models import FailureType
from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.conftest import read_stream, stream_errors
from unit_tests.mock_server.request_builder import DatadogRequestBuilder
from unit_tests.mock_server.response_builder import DatadogPaginatedResponseBuilder, datadog_error


# Datadog removed this endpoint, and the next major release replaces the stream. These tests record what
# the stream does until then.
class TestIncidentTeamsStream(TestCase):
    @HttpMocker()
    def test_fails_on_the_404_of_the_removed_endpoint(self, http_mocker: HttpMocker) -> None:
        request = DatadogRequestBuilder.incident_teams_endpoint().build()
        http_mocker.get(request, datadog_error(404, ["Not found"]))

        output = read_stream("incident_teams", expecting_error=True)

        assert output.records == []
        assert [error.failure_type for error in stream_errors(output, "incident_teams")] == [FailureType.system_error]
        http_mocker.assert_number_of_calls(request, 1)

    @HttpMocker()
    def test_reads_an_empty_page(self, http_mocker: HttpMocker) -> None:
        request = DatadogRequestBuilder.incident_teams_endpoint().build()
        http_mocker.get(request, DatadogPaginatedResponseBuilder("data").build())

        output = read_stream("incident_teams")

        assert output.errors == []
        assert output.records == []
        http_mocker.assert_number_of_calls(request, 1)

    @HttpMocker()
    def test_reads_the_teams_of_a_page_and_then_fails_on_its_page_token(self, http_mocker: HttpMocker) -> None:
        # The paginator looks for the next offset in the last record, and a team holds none.
        request = DatadogRequestBuilder.incident_teams_endpoint().build()
        http_mocker.get(request, DatadogPaginatedResponseBuilder("data").with_records([{"id": "team-1"}, {"id": "team-2"}]).build())

        output = read_stream("incident_teams", expecting_error=True)

        assert [message.record.data["id"] for message in output.records] == ["team-1", "team-2"]
        assert [error.failure_type for error in stream_errors(output, "incident_teams")] == [FailureType.system_error]
        http_mocker.assert_number_of_calls(request, 1)
