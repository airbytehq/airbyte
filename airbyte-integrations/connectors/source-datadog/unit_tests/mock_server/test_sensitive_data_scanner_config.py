# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import logging
from unittest import TestCase

from airbyte_cdk.models import FailureType
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from unit_tests.conftest import CONFIG, get_source, read_stream, stream_errors
from unit_tests.mock_server.request_builder import DatadogRequestBuilder
from unit_tests.mock_server.response_builder import datadog_error


GROUP = {
    "id": "group-1",
    "type": "sensitive_data_scanner_group",
    "attributes": {"name": "Payments", "is_enabled": True, "filter": {"query": "service:payments"}, "product_list": ["logs"]},
    "relationships": {
        "configuration": {"data": {"id": "configuration-1", "type": "sensitive_data_scanner_configuration"}},
        "rules": {"data": [{"id": "rule-1", "type": "sensitive_data_scanner_rule"}]},
    },
}
RULE = {
    "id": "rule-1",
    "type": "sensitive_data_scanner_rule",
    "attributes": {"name": "Card number", "is_enabled": True, "priority": 1, "text_replacement": {"type": "hash"}},
    "relationships": {"group": {"data": {"id": "group-1", "type": "sensitive_data_scanner_group"}}},
}
CONFIGURATION = {
    "id": "configuration-1",
    "type": "sensitive_data_scanner_configuration",
    "attributes": {},
    "relationships": {"groups": {"data": [{"id": "group-1", "type": "sensitive_data_scanner_group"}]}},
}


def _request() -> DatadogRequestBuilder:
    return DatadogRequestBuilder("v2/sensitive-data-scanner/config")


class TestSensitiveDataScannerConfigStream(TestCase):
    @HttpMocker()
    def test_reads_the_configuration_as_one_record_with_its_groups_and_rules(self, http_mocker: HttpMocker) -> None:
        # `ListScanningGroups` answers with the one configuration under `data`, and the groups and rules under
        # `included`. No other endpoint lists the groups or the rules.
        request = _request().build()
        http_mocker.get(request, HttpResponse(json.dumps({"data": CONFIGURATION, "included": [GROUP, RULE], "meta": {}})))

        output = read_stream("sensitive_data_scanner_config")

        assert output.errors == []
        assert [message.record.data for message in output.records] == [{**CONFIGURATION, "included": [GROUP, RULE], "meta": {}}]
        http_mocker.assert_number_of_calls(request, 1)

    @HttpMocker()
    def test_reads_a_configuration_without_groups(self, http_mocker: HttpMocker) -> None:
        configuration = {**CONFIGURATION, "relationships": {"groups": {"data": []}}}
        http_mocker.get(_request().build(), HttpResponse(json.dumps({"data": configuration, "included": [], "meta": {}})))

        output = read_stream("sensitive_data_scanner_config")

        assert output.errors == []
        assert [message.record.data for message in output.records] == [{**configuration, "included": [], "meta": {}}]

    def test_declares_id_as_the_primary_key(self) -> None:
        catalog = get_source().discover(logging.getLogger("airbyte"), CONFIG)

        assert [stream.source_defined_primary_key for stream in catalog.streams if stream.name == "sensitive_data_scanner_config"] == [
            [["id"]]
        ]

    @HttpMocker()
    def test_missing_permission_names_data_scanner_read(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_request().build(), datadog_error(403, ["Forbidden", "Failed permission authorization checks"]))

        output = read_stream("sensitive_data_scanner_config", expecting_error=True)

        assert [(error.failure_type, error.message) for error in stream_errors(output, "sensitive_data_scanner_config")] == [
            (
                FailureType.config_error,
                "The Application Key lacks the data_scanner_read permission: Forbidden, Failed permission authorization checks. "
                "Grant data_scanner_read to the Application Key in Datadog.",
            )
        ]
