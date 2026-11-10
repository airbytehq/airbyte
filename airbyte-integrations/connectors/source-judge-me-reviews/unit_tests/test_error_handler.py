# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server tests for the `reviews` stream error handler."""

import json
from pathlib import Path
from typing import Any
from unittest import TestCase
from unittest.mock import MagicMock, patch

import yaml
from unit_tests.conftest import _YAML_FILE_PATH, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_STREAM_NAME = "reviews"
_CONFIG = {"api_key": "test_api_key", "shop_domain": "example.myshopify.com", "start_date": "2024-01-01T00:00:00Z"}
_MAX_RETRIES = 5
_BACKOFF_SECONDS = 2
_REVIEWS_REQUEST = HttpRequest(
    "https://api.judge.me/api/v1/reviews",
    query_params={
        "shop_domain": "example.myshopify.com",
        "api_token": "test_api_key",
        "page": "1",
        "per_page": "100",
    },
)


def _review() -> dict[str, Any]:
    return {"id": 1, "updated_at": "2024-06-01T00:00:00+00:00"}


def _review_response(status_code: int = 200) -> HttpResponse:
    return HttpResponse(body=json.dumps({"reviews": [_review()]}), status_code=status_code)


def _read(expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    return read(get_source(config=_CONFIG), _CONFIG, catalog, expecting_exception=expecting_exception)


def _assert_retry_delays(sleep_mock: MagicMock, expected_count: int) -> None:
    sleep_durations = [call.args[0] for call in sleep_mock.call_args_list]
    # The CDK HttpClient adds 1s to the user-defined backoff.
    retry_delays = [duration for duration in sleep_durations if duration != 0]
    assert len(retry_delays) == expected_count
    assert retry_delays == [_BACKOFF_SECONDS + 1] * expected_count


class TestJudgeMeReviewsErrorHandler(TestCase):
    def test_reviews_error_handler_is_a_direct_default_error_handler(self) -> None:
        manifest_text = Path(_YAML_FILE_PATH).read_text()
        manifest = yaml.safe_load(manifest_text)
        error_handler = manifest["definitions"]["streams"]["reviews"]["retriever"]["requester"]["error_handler"]

        assert error_handler["type"] == "DefaultErrorHandler"
        assert error_handler["backoff_strategies"] == [{"type": "ConstantBackoffStrategy", "backoff_time_in_seconds": 2}]
        assert "Composite" + "ErrorHandler" not in manifest_text

    @HttpMocker()
    def test_5xx_is_retried_then_succeeds(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _REVIEWS_REQUEST,
            [
                HttpResponse(body="", status_code=500),
                HttpResponse(body="", status_code=503),
                _review_response(),
            ],
        )

        with patch("time.sleep", new_callable=MagicMock) as sleep_mock:
            output = _read()

        assert len(output.records) == 1
        assert output.errors == []
        http_mocker.assert_number_of_calls(_REVIEWS_REQUEST, 3)
        _assert_retry_delays(sleep_mock, 2)

    @HttpMocker()
    def test_429_is_retried_then_succeeds(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _REVIEWS_REQUEST,
            [HttpResponse(body="", status_code=429), _review_response()],
        )

        with patch("time.sleep", new_callable=MagicMock) as sleep_mock:
            output = _read()

        assert len(output.records) == 1
        assert output.errors == []
        http_mocker.assert_number_of_calls(_REVIEWS_REQUEST, 2)
        _assert_retry_delays(sleep_mock, 1)

    @HttpMocker()
    def test_persistent_5xx_stops_after_max_retries(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_REVIEWS_REQUEST, HttpResponse(body="", status_code=500))

        with patch("time.sleep", new_callable=MagicMock) as sleep_mock:
            output = _read(expecting_exception=True)

        assert output.records == []
        assert output.errors
        http_mocker.assert_number_of_calls(_REVIEWS_REQUEST, _MAX_RETRIES + 1)
        _assert_retry_delays(sleep_mock, _MAX_RETRIES)

    @HttpMocker()
    def test_403_fails_without_retry(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_REVIEWS_REQUEST, HttpResponse(body="", status_code=403))

        output = _read(expecting_exception=True)

        assert output.records == []
        assert output.errors
        http_mocker.assert_number_of_calls(_REVIEWS_REQUEST, 1)
