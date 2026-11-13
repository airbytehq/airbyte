# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Tests for Shortcut error handling."""

import json
from pathlib import Path
from typing import Any
from unittest import TestCase
from unittest.mock import patch

import pytest
import yaml

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import get_source


_CONFIG = {"api_key_2": "key", "start_date": "2024-01-01T00:00:00Z"}
_MANIFEST_PATH = Path(__file__).parents[1] / "manifest.yaml"
_MANIFEST = yaml.safe_load(_MANIFEST_PATH.read_text())
_STREAM_NAMES = sorted(_MANIFEST["definitions"]["streams"])
_EXPECTED_ERROR_HANDLER = {
    "type": "DefaultErrorHandler",
    "max_retries": 3,
    "backoff_strategies": [{"type": "ExponentialBackoffStrategy", "factor": 2}],
    "response_filters": [
        {
            "type": "HttpResponseFilter",
            "action": "RATE_LIMITED",
            "http_codes": [429],
            "error_message": "Rate limit hit",
        }
    ],
}


def _find_error_handlers(node: Any) -> list[dict[str, Any]]:
    if isinstance(node, dict):
        found = [node["error_handler"]] if "error_handler" in node else []
        return found + [handler for value in node.values() for handler in _find_error_handlers(value)]
    if isinstance(node, list):
        return [handler for value in node for handler in _find_error_handlers(value)]
    return []


def test_every_error_handler_is_a_default_error_handler() -> None:
    error_handlers = _find_error_handlers(_MANIFEST)

    assert len(error_handlers) == 24
    assert {handler["type"] for handler in error_handlers} == {"DefaultErrorHandler"}


def test_all_streams_are_covered() -> None:
    assert len(_STREAM_NAMES) == 24


@pytest.mark.parametrize("stream_name", _STREAM_NAMES)
def test_stream_uses_default_error_handler(stream_name: str) -> None:
    error_handler = _MANIFEST["definitions"]["streams"][stream_name]["retriever"]["requester"]["error_handler"]

    assert error_handler == _EXPECTED_ERROR_HANDLER


def _read_stream(stream_name: str) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(config=_CONFIG), config=_CONFIG, catalog=catalog)


def _assert_rate_limited_request_retries_and_reads_records(
    stream_name: str, url: str, record: dict[str, Any], http_mocker: HttpMocker
) -> None:
    request = HttpRequest(url)
    http_mocker.get(
        request,
        [
            HttpResponse(body='{"message": "rate limited"}', status_code=429),
            HttpResponse(body=json.dumps([record]), status_code=200),
        ],
    )

    with patch("time.sleep"):
        output = _read_stream(stream_name)

    assert len(output.records) == 1
    assert output.errors == []
    http_mocker.assert_number_of_calls(request, 2)


class ErrorHandlerTest(TestCase):
    @HttpMocker()
    def test_categories_retry_after_rate_limit(self, http_mocker: HttpMocker) -> None:
        _assert_rate_limited_request_retries_and_reads_records(
            "categories",
            "https://api.app.shortcut.com/api/v3/categories",
            {"id": 1, "updated_at": "2024-06-01T00:00:00Z"},
            http_mocker,
        )

    @HttpMocker()
    def test_labels_retry_after_rate_limit(self, http_mocker: HttpMocker) -> None:
        _assert_rate_limited_request_retries_and_reads_records(
            "labels",
            "https://api.app.shortcut.com/api/v3/labels",
            {"id": 1, "updated_at": "2024-06-01T00:00:00Z"},
            http_mocker,
        )
