#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import patch

from conftest import get_source
from requests import Request

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    HTTPAPIBudget as HTTPAPIBudgetModel,
)
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import (
    ModelToComponentFactory,
)
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


_BASE_URL = "https://www.googleapis.com/youtube/v3"
_CONFIG = {
    "credentials": {"auth_method": "api_key", "api_key": "test-api-key"},
    "channel_ids": ["UC_test"],
}


def _read_stream(stream_name: str, config: dict = _CONFIG):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(config), config, catalog)


def _error_body(reason: str) -> dict:
    return {
        "error": {
            "code": 403,
            "message": "The request cannot be completed.",
            "errors": [{"domain": "youtube", "reason": reason, "message": reason}],
        }
    }


def _http_response(body: dict, status_code: int = 200) -> HttpResponse:
    return HttpResponse(body=json.dumps(body), status_code=status_code)


def _assert_traced_error(output, failure_type: FailureType, message_substring: str) -> None:
    assert any(error.trace.error.failure_type == failure_type and message_substring in error.trace.error.message for error in output.errors)


@HttpMocker()
def test_quota_exceeded_emits_transient_error(http_mocker: HttpMocker):
    http_mocker.get(
        HttpRequest(f"{_BASE_URL}/search", query_params=ANY_QUERY_PARAMS),
        _http_response(_error_body("quotaExceeded"), status_code=403),
    )

    with patch("time.sleep"):
        output = _read_stream("videos")

    _assert_traced_error(output, FailureType.transient_error, "YouTube Data API quota")


@HttpMocker()
def test_invalid_credentials_emits_config_error(http_mocker: HttpMocker):
    http_mocker.get(
        HttpRequest(f"{_BASE_URL}/search", query_params=ANY_QUERY_PARAMS),
        _http_response({"error": {"code": 401}}, status_code=401),
    )

    with patch("time.sleep"):
        output = _read_stream("videos")

    _assert_traced_error(
        output,
        FailureType.config_error,
        "Verify the API key or OAuth credentials in the source settings.",
    )


@HttpMocker()
def test_api_not_enabled_emits_config_error(http_mocker: HttpMocker):
    http_mocker.get(
        HttpRequest(f"{_BASE_URL}/search", query_params=ANY_QUERY_PARAMS),
        _http_response(_error_body("accessNotConfigured"), status_code=403),
    )

    with patch("time.sleep"):
        output = _read_stream("videos")

    _assert_traced_error(output, FailureType.config_error, "Enable the API in that project.")


@HttpMocker()
def test_comments_disabled_ignores_comment_stream_error(http_mocker: HttpMocker):
    http_mocker.get(
        HttpRequest(f"{_BASE_URL}/search", query_params=ANY_QUERY_PARAMS),
        _http_response({"items": [{"id": {"videoId": "vid1"}}]}),
    )
    http_mocker.get(
        HttpRequest(f"{_BASE_URL}/commentThreads", query_params=ANY_QUERY_PARAMS),
        _http_response(_error_body("commentsDisabled"), status_code=403),
    )

    with patch("time.sleep"):
        output = _read_stream("comments")

    assert output.errors == []
    assert output.records == []


@HttpMocker()
def test_rate_limit_exceeded_retries_and_returns_records(http_mocker: HttpMocker):
    search_request = HttpRequest(
        f"{_BASE_URL}/search",
        query_params=ANY_QUERY_PARAMS,
    )
    http_mocker.get(
        search_request,
        [
            _http_response(_error_body("rateLimitExceeded"), status_code=403),
            _http_response({"items": [{"id": {"videoId": "vid1"}}]}),
        ],
    )

    with patch("time.sleep"):
        output = _read_stream("videos")

    assert len(output.records) == 1
    assert output.errors == []
    http_mocker.assert_number_of_calls(search_request, 2)


def test_api_budget_assigns_endpoint_weights():
    source = get_source(_CONFIG)
    factory = ModelToComponentFactory()
    budget = factory.create_component(
        model_type=HTTPAPIBudgetModel,
        component_definition=source.resolved_manifest["api_budget"],
        config=_CONFIG,
    )
    policy = budget._policies[0]

    search_request = Request(
        "GET",
        f"{_BASE_URL}/search?part=snippet",
    ).prepare()
    videos_request = Request(
        "GET",
        f"{_BASE_URL}/videos?part=snippet",
    ).prepare()

    assert policy.get_weight(search_request) == 100
    assert policy.get_weight(videos_request) == 1
