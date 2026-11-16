# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Tests for Ticketmaster error handling."""

import json
from pathlib import Path
from typing import Any
from unittest import TestCase
from unittest.mock import patch

import pytest
import yaml
from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_CONFIG = {"api_key": "key"}
_MANIFEST_PATH = Path(__file__).parents[1] / "manifest.yaml"
_RESPONSE_FILTER = {
    "type": "HttpResponseFilter",
    "action": "RATE_LIMITED",
    "http_codes": [429],
    "error_message": "Rate limits has been hit",
}


@pytest.mark.parametrize("stream_name", ["events", "attractions", "venues", "suggest", "event_images"])
def test_streams_use_default_error_handler(stream_name: str) -> None:
    manifest = yaml.safe_load(_MANIFEST_PATH.read_text())
    error_handler = manifest["definitions"]["streams"][stream_name]["retriever"]["requester"]["error_handler"]

    assert error_handler == {
        "type": "DefaultErrorHandler",
        "max_retries": 2,
        "backoff_strategies": [{"type": "ConstantBackoffStrategy", "backoff_time_in_seconds": 5}],
        "response_filters": [_RESPONSE_FILTER],
    }


def _read_stream(stream_name: str) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(config=_CONFIG), config=_CONFIG, catalog=catalog)


def _assert_rate_limited_request_retries_and_reads_records(
    stream_name: str, request: HttpRequest, body: dict[str, Any], http_mocker: HttpMocker
) -> None:
    http_mocker.get(
        request,
        [
            HttpResponse(body='{"error": "rate limited"}', status_code=429),
            HttpResponse(body=json.dumps(body), status_code=200),
        ],
    )

    with patch("time.sleep"):
        output = _read_stream(stream_name)

    assert len(output.records) == 1
    assert output.errors == []
    http_mocker.assert_number_of_calls(request, 2)


class ErrorHandlerTest(TestCase):
    @HttpMocker()
    def test_venues_retry_after_rate_limit(self, http_mocker: HttpMocker) -> None:
        _assert_rate_limited_request_retries_and_reads_records(
            "venues",
            HttpRequest(
                url="https://app.ticketmaster.com/discovery/v2/venues",
                query_params={"apikey": "key", "size": "100"},
            ),
            {
                "_embedded": {"venues": [{"id": "v1"}]},
                "page": {"number": 0, "size": 100, "totalPages": 1},
            },
            http_mocker,
        )

    @HttpMocker()
    def test_suggest_retry_after_rate_limit(self, http_mocker: HttpMocker) -> None:
        _assert_rate_limited_request_retries_and_reads_records(
            "suggest",
            HttpRequest(
                url="https://app.ticketmaster.com/discovery/v2/suggest",
                query_params={"apikey": "key"},
            ),
            {"_embedded": {"venues": [{"id": "v1"}]}},
            http_mocker,
        )
