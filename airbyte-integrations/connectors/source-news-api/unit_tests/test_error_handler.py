# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path

import yaml
from unit_tests.conftest import get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


_MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"
_COMPOSITE_ERROR_HANDLER_TYPE = "Composite" + "ErrorHandler"
_URL_BASE = "https://newsapi.org/v2"
_CONFIG = {
    "api_key": "test-api-key",
    "search_query": "airbyte",
    "country": "us",
    "category": "technology",
    "sort_by": "publishedAt",
    "start_date": "2025-01-01",
    "end_date": "2025-01-02",
    "language": "en",
}
_ARTICLES_RESPONSE = {
    "status": "ok",
    "totalResults": 1,
    "articles": [
        {
            "source": {"id": "test-source", "name": "Test Source"},
            "author": "Author",
            "title": "A test article",
            "description": "An article used by the unit test.",
            "url": "https://example.com/article",
            "publishedAt": "2025-01-01T12:00:00Z",
            "content": "Article content",
        }
    ],
}


def _contains_composite_error_handler(node: object) -> bool:
    if isinstance(node, dict):
        return node.get("type") == _COMPOSITE_ERROR_HANDLER_TYPE or any(_contains_composite_error_handler(value) for value in node.values())
    if isinstance(node, list):
        return any(_contains_composite_error_handler(value) for value in node)
    return False


def test_manifest_uses_default_error_handlers_directly() -> None:
    manifest = yaml.safe_load(_MANIFEST_PATH.read_text())

    assert not _contains_composite_error_handler(manifest)
    for stream in manifest["definitions"]["streams"].values():
        assert stream["retriever"]["requester"]["error_handler"]["type"] == "DefaultErrorHandler"
    for stream in manifest["streams"]:
        assert stream["retriever"]["requester"]["error_handler"]["type"] == "DefaultErrorHandler"


def _read_stream(stream_name: str, response: dict, status_code: int):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    request = HttpRequest(f"{_URL_BASE}/{stream_name.replace('_', '-')}", query_params=ANY_QUERY_PARAMS)
    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(json.dumps(response), status_code))
        output = read(get_source(config=_CONFIG), _CONFIG, catalog)
        http_mocker.assert_number_of_calls(request, 1)
    return output


def _config_error_message(output, expected_message: str) -> str:
    errors = [
        message.trace.error for message in output.errors if message.trace.error and expected_message in (message.trace.error.message or "")
    ]
    assert len(errors) == 1, output.errors
    error = errors[0]
    assert error.failure_type == FailureType.config_error
    return error.message or ""


def test_everything_success_emits_records() -> None:
    output = _read_stream("everything", _ARTICLES_RESPONSE, 200)

    assert len(output.records) == 1
    assert output.records[0].record.data["title"] == "A test article"
    assert output.errors == []


def test_everything_maximum_results_reached_is_ignored() -> None:
    output = _read_stream(
        "everything",
        {"status": "error", "code": "maximumResultsReached", "message": "Too many results."},
        426,
    )

    assert output.records == []
    assert output.errors == []


def test_everything_parameters_missing_is_a_config_error() -> None:
    output = _read_stream(
        "everything",
        {"status": "error", "code": "parametersMissing", "message": "Required parameters are missing."},
        400,
    )

    message = _config_error_message(output, "News API rejected the `everything` request:")
    assert "requires at least one of `search_query`" in message


def test_top_headlines_upgrade_required_is_a_config_error() -> None:
    message = "Your plan does not include the top headlines endpoint."
    output = _read_stream(
        "top_headlines",
        {"status": "error", "code": "upgradeRequired", "message": message},
        426,
    )

    assert f"News API rejected the `top_headlines` request: {message}" in _config_error_message(
        output, "News API rejected the `top_headlines` request:"
    )
