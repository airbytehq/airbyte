# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
from unittest import TestCase

from airbyte_cdk.models import FailureType
from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.conftest import CONFIG, get_source, read_stream, stream_errors
from unit_tests.mock_server.request_builder import DatadogRequestBuilder
from unit_tests.mock_server.response_builder import DatadogPaginatedResponseBuilder, datadog_error


def _request() -> DatadogRequestBuilder:
    return DatadogRequestBuilder("v1/synthetics/locations")


class TestSyntheticsLocationsStream(TestCase):
    @HttpMocker()
    def test_reads_every_location_in_one_request(self, http_mocker: HttpMocker) -> None:
        # `ListLocations` takes no parameter and returns the public and the private locations together.
        locations = [
            {"id": "aws:eu-central-1", "name": "Frankfurt (AWS)"},
            {"id": "pl:office-berlin-1a2b3c", "name": "Berlin office"},
        ]
        request = _request().build()
        http_mocker.get(request, DatadogPaginatedResponseBuilder("locations").with_records(locations).build())

        output = read_stream("synthetics_locations")

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == ["aws:eu-central-1", "pl:office-berlin-1a2b3c"]
        http_mocker.assert_number_of_calls(request, 1)

    def test_declares_the_location_id_as_the_primary_key(self) -> None:
        catalog = get_source().discover(logging.getLogger("airbyte"), CONFIG)

        assert next(stream.source_defined_primary_key for stream in catalog.streams if stream.name == "synthetics_locations") == [["id"]]

    @HttpMocker()
    def test_a_missing_permission_names_synthetics_private_location_read(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_request().build(), datadog_error(403, ["Forbidden", "Failed permission authorization checks"]))

        output = read_stream("synthetics_locations", expecting_error=True)

        assert [(error.failure_type, error.message) for error in stream_errors(output, "synthetics_locations")] == [
            (
                FailureType.config_error,
                "The Application Key lacks the synthetics_private_location_read permission: Forbidden, Failed permission "
                "authorization checks. Grant synthetics_private_location_read to the Application Key in Datadog.",
            )
        ]
