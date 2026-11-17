# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import logging
from unittest import TestCase

from airbyte_cdk.models import FailureType
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from unit_tests.conftest import CONFIG, get_source, read_stream, stream_errors
from unit_tests.mock_server.request_builder import DatadogRequestBuilder
from unit_tests.mock_server.response_builder import datadog_error


def _request() -> DatadogRequestBuilder:
    return DatadogRequestBuilder("v1/org")


class TestOrganizationStream(TestCase):
    @HttpMocker()
    def test_reads_the_organization_in_one_request(self, http_mocker: HttpMocker) -> None:
        # `ListOrgs` takes no parameter and returns the organization of the keys.
        organization = {
            "public_id": "abc123def456",
            "name": "Test org",
            "created": "2026-11-12 10:00:00",
            "settings": {"saml": {"enabled": False}, "saml_strict_mode": {"enabled": False}, "private_widget_share": False},
        }
        request = _request().build()
        http_mocker.get(request, HttpResponse(json.dumps({"orgs": [organization]})))

        output = read_stream("organization")

        assert output.errors == []
        assert [message.record.data for message in output.records] == [organization]
        http_mocker.assert_number_of_calls(request, 1)

    def test_declares_the_public_id_as_the_primary_key(self) -> None:
        catalog = get_source().discover(logging.getLogger("airbyte"), CONFIG)

        assert next(stream.source_defined_primary_key for stream in catalog.streams if stream.name == "organization") == [["public_id"]]

    @HttpMocker()
    def test_a_missing_permission_names_org_management(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_request().build(), datadog_error(403, ["Forbidden", "Failed permission authorization checks"]))

        output = read_stream("organization", expecting_error=True)

        assert [(error.failure_type, error.message) for error in stream_errors(output, "organization")] == [
            (
                FailureType.config_error,
                "The Application Key lacks the org_management permission: Forbidden, Failed permission authorization checks. "
                "Grant org_management to the Application Key in Datadog.",
            )
        ]
