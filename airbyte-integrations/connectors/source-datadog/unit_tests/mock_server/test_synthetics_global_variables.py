# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
from unittest import TestCase

from airbyte_cdk.models import FailureType
from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.conftest import CONFIG, get_source, read_stream, stream_errors
from unit_tests.mock_server.request_builder import DatadogRequestBuilder
from unit_tests.mock_server.response_builder import DatadogPaginatedResponseBuilder, datadog_error


# Datadog leaves out the value of a secure variable, and returns the value of every other one, a TOTP seed included.
VARIABLES = [
    {"id": "plain", "name": "LOGIN_USER", "is_totp": False, "value": {"secure": False, "value": "qa-user@example.com"}},
    {"id": "secure", "name": "LOGIN_PASSWORD", "is_totp": False, "value": {"secure": True}},
    {
        "id": "totp",
        "name": "MFA_SEED",
        "is_totp": True,
        "value": {"secure": False, "value": "JBSWY3DPEHPK3PXP", "options": {"totp_parameters": {"digits": 6, "refresh_interval": 30}}},
    },
    {"id": "no-value", "name": "PARSED_TOKEN", "parse_test_public_id": "abc-def-ghi", "value": None},
]


def _request() -> DatadogRequestBuilder:
    return DatadogRequestBuilder("v1/synthetics/variables")


class TestSyntheticsGlobalVariablesStream(TestCase):
    @HttpMocker()
    def test_reads_every_variable_in_one_request(self, http_mocker: HttpMocker) -> None:
        # `ListGlobalVariables` takes no paging parameter.
        request = _request().build()
        http_mocker.get(request, DatadogPaginatedResponseBuilder("variables").with_records(VARIABLES).build())

        output = read_stream("synthetics_global_variables")

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == ["plain", "secure", "totp", "no-value"]
        http_mocker.assert_number_of_calls(request, 1)

    @HttpMocker()
    def test_never_emits_the_value_of_a_variable(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_request().build(), DatadogPaginatedResponseBuilder("variables").with_records(VARIABLES).build())

        output = read_stream("synthetics_global_variables")

        values = {message.record.data["id"]: message.record.data.get("value") for message in output.records}
        assert output.errors == []
        assert values == {
            "plain": {"secure": False},
            "secure": {"secure": True},
            "totp": {"secure": False, "options": {"totp_parameters": {"digits": 6, "refresh_interval": 30}}},
            "no-value": None,
        }

    def test_declares_no_variable_value(self) -> None:
        catalog = get_source().discover(logging.getLogger("airbyte"), CONFIG)

        schema = next(stream.json_schema for stream in catalog.streams if stream.name == "synthetics_global_variables")
        assert "value" not in schema["properties"]["value"]["properties"]

    def test_declares_the_variable_id_as_the_primary_key(self) -> None:
        catalog = get_source().discover(logging.getLogger("airbyte"), CONFIG)

        assert next(stream.source_defined_primary_key for stream in catalog.streams if stream.name == "synthetics_global_variables") == [
            ["id"]
        ]

    @HttpMocker()
    def test_a_missing_permission_names_synthetics_global_variable_read(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_request().build(), datadog_error(403, ["Forbidden", "Failed permission authorization checks"]))

        output = read_stream("synthetics_global_variables", expecting_error=True)

        assert [(error.failure_type, error.message) for error in stream_errors(output, "synthetics_global_variables")] == [
            (
                FailureType.config_error,
                "The Application Key lacks the synthetics_global_variable_read permission: Forbidden, Failed permission "
                "authorization checks. Grant synthetics_global_variable_read to the Application Key in Datadog.",
            )
        ]
