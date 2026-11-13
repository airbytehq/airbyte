# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest

from airbyte_cdk.models import FailureType
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse

from .helpers import config, read_stream, request


@pytest.mark.parametrize("stream", ["market_chart", "history"])
def test_public_api_historical_limit_is_config_error(stream: str) -> None:
    with HttpMocker() as mocker:
        expected_request = request(stream, date="01-11-2026" if stream == "history" else None)
        mocker.get(
            expected_request,
            HttpResponse(
                json.dumps({"error": {"status": {"error_code": 10012, "error_message": "Your request exceeds the allowed time range."}}}),
                401,
            ),
        )
        test_config = config()
        test_config["end_date"] = "2026-11-02"
        output = read_stream(stream, test_config, expecting_exception=True)
        assert output.records == []
        assert len(output.errors) == 2
        assert all(message.trace.error.failure_type == FailureType.config_error for message in output.errors)
        error = output.errors[0].trace.error
        assert error.failure_type == FailureType.config_error
        assert error.message == (
            "CoinGecko public (free) API users can only query historical data within "
            "the past 365 days. Choose a more recent start_date / smaller `days` "
            "value, or provide a CoinGecko Pro API key."
        )
        mocker.assert_number_of_calls(expected_request, 1)
