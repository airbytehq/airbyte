# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest

from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse

from .helpers import config, read_stream, request


@pytest.mark.parametrize("api_key", ["", "test-pro-key"])
@pytest.mark.parametrize(
    "payload",
    [{"prices": [[1793491200000, 69000]], "market_caps": [[1793491200000, 1300000]], "total_volumes": [[1793491200000, 42000]]}, []],
)
def test_market_chart_full_refresh(api_key: str, payload: dict | list) -> None:
    with HttpMocker() as mocker:
        expected_request = request("market_chart", api_key)
        mocker.get(expected_request, HttpResponse(json.dumps(payload), 200))
        output = read_stream("market_chart", config(api_key))
        assert [message.record.data for message in output.records] == ([payload] if payload else [])
        assert output.most_recent_state.stream_state.__dict__ == {"__ab_no_cursor_state_message": True}
        assert output.errors == []
        mocker.assert_number_of_calls(expected_request, 1)
