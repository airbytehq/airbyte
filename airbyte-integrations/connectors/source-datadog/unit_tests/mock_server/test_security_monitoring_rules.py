# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
from unittest import TestCase

from airbyte_cdk.models import FailureType
from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.conftest import CONFIG, get_source, read_stream, stream_errors
from unit_tests.mock_server.request_builder import DatadogRequestBuilder
from unit_tests.mock_server.response_builder import DatadogPaginatedResponseBuilder, datadog_error


def _request() -> DatadogRequestBuilder:
    # `ListSecurityMonitoringRules`: `page[size]` "The maximum allowed value is 100", and `page[number]` starts at 0.
    return DatadogRequestBuilder("v2/security_monitoring/rules").with_query_param("page[size]", 100)


def _page(rule_ids: list[str], total_count: int) -> DatadogPaginatedResponseBuilder:
    return (
        DatadogPaginatedResponseBuilder("data")
        .with_records([{"id": rule_id} for rule_id in rule_ids])
        .with_meta({"page": {"total_count": total_count, "total_filtered_count": total_count}})
    )


class TestSecurityMonitoringRulesStream(TestCase):
    @HttpMocker()
    def test_reads_two_pages_and_ends_after_the_short_one(self, http_mocker: HttpMocker) -> None:
        full_page = [f"rule-{number}" for number in range(100)]
        first_request = _request().build()
        second_request = _request().with_query_param("page[number]", 1).build()
        http_mocker.get(first_request, _page(full_page, 101).build())
        http_mocker.get(second_request, _page(["rule-100"], 101).build())

        output = read_stream("security_monitoring_rules")

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == full_page + ["rule-100"]
        http_mocker.assert_number_of_calls(first_request, 1)
        http_mocker.assert_number_of_calls(second_request, 1)

    @HttpMocker()
    def test_ends_on_the_empty_page_after_a_full_last_page(self, http_mocker: HttpMocker) -> None:
        full_page = [f"rule-{number}" for number in range(100)]
        empty_page = _request().with_query_param("page[number]", 1).build()
        http_mocker.get(_request().build(), _page(full_page, 100).build())
        http_mocker.get(empty_page, _page([], 100).build())

        output = read_stream("security_monitoring_rules")

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == full_page
        http_mocker.assert_number_of_calls(empty_page, 1)

    @HttpMocker()
    def test_passes_the_camel_case_fields_through(self, http_mocker: HttpMocker) -> None:
        rule = {
            "id": "rule-1",
            "type": "log_detection",
            "name": "Brute force",
            "isEnabled": True,
            "isDefault": True,
            "createdAt": 1700000000000,
            "cases": [{"name": "high", "status": "high", "condition": "a > 10"}],
            "options": {"evaluationWindow": 300, "keepAlive": 3600},
        }
        http_mocker.get(_request().build(), DatadogPaginatedResponseBuilder("data").with_records([rule]).build())

        output = read_stream("security_monitoring_rules")

        assert output.errors == []
        assert [message.record.data for message in output.records] == [rule]

    def test_declares_id_as_the_primary_key(self) -> None:
        catalog = get_source().discover(logging.getLogger("airbyte"), CONFIG)

        assert [stream.source_defined_primary_key for stream in catalog.streams if stream.name == "security_monitoring_rules"] == [[["id"]]]

    @HttpMocker()
    def test_missing_permission_names_security_monitoring_rules_read(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_request().build(), datadog_error(403, ["Forbidden", "Failed permission authorization checks"]))

        output = read_stream("security_monitoring_rules", expecting_error=True)

        assert [(error.failure_type, error.message) for error in stream_errors(output, "security_monitoring_rules")] == [
            (
                FailureType.config_error,
                "The Application Key lacks the security_monitoring_rules_read permission: Forbidden, Failed permission authorization "
                "checks. Grant security_monitoring_rules_read to the Application Key in Datadog.",
            )
        ]
