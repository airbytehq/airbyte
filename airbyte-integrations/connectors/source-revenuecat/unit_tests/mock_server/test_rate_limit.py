# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""429 responses are retried after the vendor's Retry-After, not the CDK's 1-2-4-8-16 s default."""

import json
import time

from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from mock_server.helpers import read_stream, records_data
from mock_server.request_builder import RevenueCatRequestBuilder
from mock_server.streams import PROJECT_ID, list_response, record


def test_429_waits_for_retry_after_then_reads(monkeypatch) -> None:
    sleeps = []
    monkeypatch.setattr(time, "sleep", sleeps.append)
    rate_limited = HttpResponse(
        body=json.dumps({"object": "error", "type": "rate_limit_error", "retryable": True, "backoff_ms": 45000}),
        status_code=429,
        headers={"Retry-After": "45"},
    )
    request = RevenueCatRequestBuilder.endpoint("/projects").build()
    with HttpMocker() as http_mocker:
        http_mocker.get(request, [rate_limited, list_response("projects", [record("projects", PROJECT_ID)])])
        output = read_stream("projects")

    assert output.errors == []
    assert [r["id"] for r in records_data(output)] == [PROJECT_ID]
    assert sum(sleeps) == 46
    http_mocker.assert_number_of_calls(request, 2)
