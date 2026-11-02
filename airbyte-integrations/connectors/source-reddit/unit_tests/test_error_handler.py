# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict, Iterable
from unittest import TestCase
from unittest.mock import patch

import pytest
import yaml

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import _YAML_FILE_PATH, get_source


_MANIFEST = yaml.safe_load(_YAML_FILE_PATH.read_text())
_STREAM_NAMES = ["search", "subreddit_search", "message_inbox", "subreddit_popular", "subreddit_explore"]
_COMPOSITE_ERROR_HANDLER = "".join(("Composite", "ErrorHandler"))
_POPULAR_REQUEST = HttpRequest(
    "https://oauth.reddit.com/subreddits/popular",
    query_params={"q": "airbyte", "exact": "False", "limit": "10", "include_over_18": "False"},
)
_EXPLORE_REQUEST = HttpRequest(
    "https://oauth.reddit.com/r/funny",
    query_params={"exact": "False", "limit": "10", "include_over_18": "False"},
)
_CONFIG: Dict[str, Any] = {
    "credentials": {"auth_type": "api_key", "api_key": "test-token"},
    "query": "airbyte",
    "exact": False,
    "limit": 10,
    "include_over_18": False,
    "start_date": "2020-01-01T00:00:00Z",
}
_MAX_RETRIES = 3


def _walk(value: Any) -> Iterable[Dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def test_manifest_contains_no_composite_error_handlers() -> None:
    assert not any(node.get("type") == _COMPOSITE_ERROR_HANDLER for node in _walk(_MANIFEST))


@pytest.mark.parametrize("stream_name", _STREAM_NAMES)
def test_stream_has_single_default_error_handler(stream_name: str) -> None:
    error_handler = _MANIFEST["definitions"]["streams"][stream_name]["retriever"]["requester"]["error_handler"]
    expected = {
        "type": "DefaultErrorHandler",
        "max_retries": _MAX_RETRIES,
        "response_filters": [
            {
                "type": "HttpResponseFilter",
                "action": "RETRY",
                "http_codes": [429],
                "error_message": "Rate limit hit... Retrying",
            }
        ],
    }
    if stream_name != "subreddit_explore":
        expected["backoff_strategies"] = [{"type": "ExponentialBackoffStrategy", "factor": 2}]

    assert error_handler == expected


def _subreddit_response() -> HttpResponse:
    body = {
        "data": {
            "after": None,
            "children": [{"kind": "t3", "data": {"id": "post-id", "created": 1760000000, "title": "A Reddit post"}}],
        }
    }
    return HttpResponse(body=json.dumps(body), status_code=200)


def _read(stream_name: str, config: Dict[str, Any] | None = None, expecting_exception: bool = False) -> EntrypointOutput:
    source_config = config or _CONFIG
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(config=source_config), source_config, catalog, expecting_exception=expecting_exception)


@patch("time.sleep", lambda _: None)
class TestRedditErrorHandler(TestCase):
    @HttpMocker()
    def test_subreddit_popular_retries_429_then_succeeds(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_POPULAR_REQUEST, [HttpResponse(body="", status_code=429), _subreddit_response()])

        output = _read("subreddit_popular")

        assert len(output.records) == 1
        assert output.errors == []
        http_mocker.assert_number_of_calls(_POPULAR_REQUEST, 2)

    @HttpMocker()
    def test_subreddit_popular_stops_after_max_retries(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_POPULAR_REQUEST, HttpResponse(body="", status_code=429))

        output = _read("subreddit_popular", expecting_exception=True)

        assert output.records == []
        assert output.errors
        http_mocker.assert_number_of_calls(_POPULAR_REQUEST, _MAX_RETRIES + 1)

    @HttpMocker()
    def test_subreddit_explore_retries_429_then_succeeds(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_EXPLORE_REQUEST, [HttpResponse(body="", status_code=429), _subreddit_response()])
        config = {**_CONFIG, "subreddits": ["funny"]}

        output = _read("subreddit_explore", config=config)

        assert len(output.records) == 1
        assert output.errors == []
        http_mocker.assert_number_of_calls(_EXPLORE_REQUEST, 2)
