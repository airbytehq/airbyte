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
    return DatadogRequestBuilder("v1/logs/config/pipelines")


class TestLogPipelinesStream(TestCase):
    @HttpMocker()
    def test_reads_every_pipeline_in_one_request(self, http_mocker: HttpMocker) -> None:
        # `ListLogsPipelines` takes no paging parameter and returns every pipeline in one bare array.
        request = _request().build()
        pipelines = [
            {
                "id": "pipeline-1",
                "type": "pipeline",
                "name": "Python",
                "filter": {"query": "source:python"},
                "processors": [{"type": "grok-parser", "name": "Parse", "source": "message", "grok": {"match_rules": "rule %{data}"}}],
            },
            {"id": "pipeline-2", "type": "integration", "name": "Nginx", "is_read_only": True, "processors": []},
        ]
        http_mocker.get(request, HttpResponse(json.dumps(pipelines)))

        output = read_stream("log_pipelines")

        assert output.errors == []
        assert [message.record.data for message in output.records] == pipelines
        http_mocker.assert_number_of_calls(request, 1)

    def test_declares_id_as_the_primary_key(self) -> None:
        catalog = get_source().discover(logging.getLogger("airbyte"), CONFIG)

        assert [stream.source_defined_primary_key for stream in catalog.streams if stream.name == "log_pipelines"] == [[["id"]]]

    @HttpMocker()
    def test_missing_permission_names_logs_read_config(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_request().build(), datadog_error(403, ["Forbidden", "Failed permission authorization checks"]))

        output = read_stream("log_pipelines", expecting_error=True)

        assert [(error.failure_type, error.message) for error in stream_errors(output, "log_pipelines")] == [
            (
                FailureType.config_error,
                "The Application Key lacks the logs_read_config permission: Forbidden, Failed permission authorization checks. "
                "Grant logs_read_config to the Application Key in Datadog.",
            )
        ]
