# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from unit_tests.conftest import read_stream
from unit_tests.mock_server.request_builder import DatadogRequestBuilder


class TestDowntimesStream(TestCase):
    @HttpMocker()
    def test_reads_the_list_in_one_request(self, http_mocker: HttpMocker) -> None:
        # The v1 list answers with a bare array and takes no paging parameter.
        request = DatadogRequestBuilder.downtimes_endpoint().build()
        http_mocker.get(request, HttpResponse(json.dumps([{"id": 1}, {"id": 2}])))

        output = read_stream("downtimes")

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == [1, 2]
        http_mocker.assert_number_of_calls(request, 1)
