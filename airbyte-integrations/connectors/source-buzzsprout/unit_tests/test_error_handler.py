# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Tests for Buzzsprout error handling."""

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


_CONFIG = {"api_key": "key", "podcast_id": "123", "start_date": "2024-01-01T00:00:00Z"}
_MANIFEST_PATH = Path(__file__).parents[1] / "manifest.yaml"
_RESPONSE_FILTER = {
    "type": "HttpResponseFilter",
    "action": "RATE_LIMITED",
    "http_codes": [429],
}


@pytest.mark.parametrize(
    ("stream_name", "error_message"),
    [("episodes", "Rate limits hit"), ("podcasts", "Rate limit hit")],
)
def test_streams_use_default_error_handler(stream_name: str, error_message: str) -> None:
    manifest = yaml.safe_load(_MANIFEST_PATH.read_text())
    error_handler = manifest["definitions"]["streams"][stream_name]["retriever"]["requester"]["error_handler"]

    assert error_handler == {
        "type": "DefaultErrorHandler",
        "max_retries": 3,
        "backoff_strategies": [{"type": "ExponentialBackoffStrategy", "factor": 2}],
        "response_filters": [{**_RESPONSE_FILTER, "error_message": error_message}],
    }


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
            HttpResponse(body='{"error": "rate limited"}', status_code=429),
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
    def test_episodes_retry_after_rate_limit(self, http_mocker: HttpMocker) -> None:
        _assert_rate_limited_request_retries_and_reads_records(
            "episodes",
            "https://www.buzzsprout.com/api/123/episodes.json",
            {"id": 1, "published_at": "2024-06-01T00:00:00.000+00:00"},
            http_mocker,
        )

    @HttpMocker()
    def test_podcasts_retry_after_rate_limit(self, http_mocker: HttpMocker) -> None:
        _assert_rate_limited_request_retries_and_reads_records(
            "podcasts",
            "https://www.buzzsprout.com/api/podcasts.json",
            {"id": 1},
            http_mocker,
        )
