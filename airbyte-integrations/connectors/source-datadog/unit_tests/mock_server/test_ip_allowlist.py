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
    return DatadogRequestBuilder("v2/ip_allowlist")


class TestIpAllowlistStream(TestCase):
    @HttpMocker()
    def test_reads_the_allowlist_as_one_record(self, http_mocker: HttpMocker) -> None:
        allowlist = {
            "type": "ip_allowlist",
            "id": "org-public-id",
            "attributes": {
                "enabled": True,
                "entries": [
                    {"data": {"type": "ip_allowlist_entry", "id": "entry-1", "attributes": {"cidr_block": "10.0.0.0/8", "note": "VPN"}}},
                    {"data": {"type": "ip_allowlist_entry", "id": "entry-2", "attributes": {"cidr_block": "192.0.2.1/32"}}},
                ],
            },
        }
        request = _request().build()
        http_mocker.get(request, HttpResponse(json.dumps({"data": allowlist})))

        output = read_stream("ip_allowlist")

        assert output.errors == []
        assert [message.record.data for message in output.records] == [allowlist]
        http_mocker.assert_number_of_calls(request, 1)

    def test_declares_the_org_id_as_the_primary_key(self) -> None:
        catalog = get_source().discover(logging.getLogger("airbyte"), CONFIG)

        assert next(stream.source_defined_primary_key for stream in catalog.streams if stream.name == "ip_allowlist") == [["id"]]

    @HttpMocker()
    def test_a_missing_permission_names_org_management(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_request().build(), datadog_error(403, ["Forbidden", "Failed permission authorization checks"]))

        output = read_stream("ip_allowlist", expecting_error=True)

        assert [(error.failure_type, error.message) for error in stream_errors(output, "ip_allowlist")] == [
            (
                FailureType.config_error,
                "The Application Key lacks the org_management permission: Forbidden, Failed permission authorization checks. "
                "Grant org_management to the Application Key in Datadog.",
            )
        ]
