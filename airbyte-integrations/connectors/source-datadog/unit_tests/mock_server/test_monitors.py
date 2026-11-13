# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from unit_tests.conftest import read_stream
from unit_tests.mock_server.request_builder import DatadogRequestBuilder


class TestMonitorsStream(TestCase):
    @HttpMocker()
    def test_reads_every_monitor_in_one_request(self, http_mocker: HttpMocker) -> None:
        # Without `page`, Datadog returns all monitors in one bare array.
        request = DatadogRequestBuilder.monitors_endpoint().build()
        http_mocker.get(request, HttpResponse(json.dumps([{"id": 1}, {"id": 2}])))

        output = read_stream("monitors")

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == [1, 2]
        http_mocker.assert_number_of_calls(request, 1)
