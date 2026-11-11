# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from conftest import get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG = {
    "apiKey": "test-api-key",
    "sort": "asc",
    "adjusted": "true",
    "stocksTicker": "AAPL",
    "multiplier": 1,
    "timespan": "day",
    "start_date": "2024-06-01",
    "end_date": "2024-06-03",
}
REQUEST = HttpRequest(
    url="https://api.polygon.io/v2/aggs/ticker/AAPL/range/1/day/2024-06-01/2024-06-03",
    query_params={"adjusted": "true", "sort": "asc", "limit": "120", "apiKey": "test-api-key"},
)
PLAN_MESSAGE = (
    "Polygon rejected the requested date range because your Polygon plan does not include data that old. "
    "Set Start Date to a date within your plan's history window, or upgrade your Polygon plan."
)
DEFAULT_MESSAGE = "HTTP Status Code: 403. Error: Forbidden. You don't have permission to access this resource."


class TestForbiddenResponses(TestCase):
    def assert_read_error(self, http_mocker: HttpMocker, body: str, expected_message: str) -> None:
        http_mocker.get(REQUEST, HttpResponse(body=body, status_code=403))
        catalog = CatalogBuilder().with_stream("stock_api", SyncMode.full_refresh).build()

        output = read(get_source(CONFIG), CONFIG, catalog, expecting_exception=True)

        assert output.records == []
        assert output.errors
        assert all(message.trace.error.failure_type == FailureType.config_error for message in output.errors)
        assert any(message.trace.error.message == expected_message for message in output.errors)
        http_mocker.assert_number_of_calls(REQUEST, 1)

    @HttpMocker()
    def test_plan_timeframe_403_is_actionable_config_error(self, http_mocker: HttpMocker) -> None:
        body = json.dumps(
            {
                "status": "NOT_AUTHORIZED",
                "request_id": "x",
                "message": "Your plan doesn't include this data timeframe. Please upgrade your plan at https://polygon.io/pricing",
            }
        )
        self.assert_read_error(http_mocker, body, PLAN_MESSAGE)

    @HttpMocker()
    def test_unrelated_403_keeps_default_error(self, http_mocker: HttpMocker) -> None:
        body = json.dumps({"status": "NOT_AUTHORIZED", "request_id": "x", "message": "Invalid API key"})
        self.assert_read_error(http_mocker, body, DEFAULT_MESSAGE)

    @HttpMocker()
    def test_empty_403_keeps_default_error(self, http_mocker: HttpMocker) -> None:
        self.assert_read_error(http_mocker, "", DEFAULT_MESSAGE)
