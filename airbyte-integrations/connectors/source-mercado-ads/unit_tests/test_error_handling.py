# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
import requests
import yaml
from conftest import _YAML_FILE_PATH, get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    CompositeErrorHandler as CompositeErrorHandlerModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    DefaultErrorHandler as DefaultErrorHandlerModel,
)
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters.error_handlers import DefaultErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG = {
    "client_id": "test-client-id",
    "client_secret": "test-client-secret",
    "client_refresh_token": "test-refresh-token",
    "lookback_days": 7,
}
TOKEN_URL = "https://api.mercadolibre.com/oauth/token"
TOKEN_REQUEST = HttpRequest(
    TOKEN_URL,
    body=(
        "grant_type=refresh_token&client_id=test-client-id&client_secret=test-client-secret"
        "&refresh_token=test-refresh-token&scopes=offline_access&scopes=read"
    ),
)
ADVERTISERS_REQUEST = HttpRequest(
    "https://api.mercadolibre.com/advertising/advertisers",
    query_params={"product_id": "DISPLAY"},
)
CAMPAIGNS_REQUEST = HttpRequest(
    "https://api.mercadolibre.com/advertising/advertisers/123/display/campaigns",
    headers={"Api-Version": "1"},
)
HANDLERS = (
    ("brand_campaigns_metrics", 401, "Advertiser has no access to campaign metrics"),
    ("brand_items", 401, "Advertiser has no access to campaign items"),
    ("brand_keywords", 401, "Advertiser has no access to campaign keyword"),
    ("brand_keywords_metrics", 401, "Advertiser has no access to campaign keyword metrics"),
    ("display_campaigns", 404, "No campaigns found for advertiser"),
    ("display_line_items", 404, "No line items found for campaign"),
    ("display_creatives", 404, "No creatives found for line_item"),
    ("product_campaigns", 404, "No campaigns found for advertiser"),
    ("product_items", 404, "No items found for campaign"),
)
CLASSIFICATIONS = {
    200: (ResponseAction.SUCCESS, None),
    400: (ResponseAction.FAIL, FailureType.system_error),
    401: (ResponseAction.FAIL, FailureType.config_error),
    403: (ResponseAction.FAIL, FailureType.config_error),
    404: (ResponseAction.FAIL, FailureType.system_error),
    429: (ResponseAction.RATE_LIMITED, FailureType.transient_error),
    500: (ResponseAction.RETRY, FailureType.transient_error),
    503: (ResponseAction.RETRY, FailureType.transient_error),
}
STATUS_CODES = tuple(CLASSIFICATIONS)


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    slept = []
    monkeypatch.setattr("time.sleep", lambda seconds=0, *_args, **_kwargs: slept.append(seconds))
    return slept


def _resolved_manifest():
    return ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(_YAML_FILE_PATH.read_text()))


def _error_handler(stream_name):
    definition = _resolved_manifest()["definitions"]["streams"][stream_name]["retriever"]["requester"]["error_handler"]
    model = CompositeErrorHandlerModel if definition.get("type") == "CompositeErrorHandler" else DefaultErrorHandlerModel
    return ModelToComponentFactory().create_component(model, definition, config={})


def _response(status_code):
    response = requests.Response()
    response.status_code = status_code
    response.request = requests.Request("GET", "https://api.mercadolibre.com/").prepare()
    response.url = response.request.url
    response.headers["Content-Type"] = "application/json"
    response._content = b"{}"
    return response


def test_manifest_has_no_composite_error_handler() -> None:
    composite_handlers = []

    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == "CompositeErrorHandler":
                composite_handlers.append(node)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(_resolved_manifest())

    assert not composite_handlers


@pytest.mark.parametrize("stream_name, ignored_code, error_message", HANDLERS)
def test_error_handler_ignores_configured_status_with_message(stream_name, ignored_code, error_message) -> None:
    handler = _error_handler(stream_name)

    assert isinstance(handler, DefaultErrorHandler)
    assert handler.max_retries == 5
    assert handler.max_time == 600

    resolution = handler.interpret_response(_response(ignored_code))

    assert resolution.response_action == ResponseAction.IGNORE
    assert resolution.error_message == error_message


@pytest.mark.parametrize(("stream_name", "ignored_code", "_error_message"), HANDLERS)
@pytest.mark.parametrize("status_code", STATUS_CODES)
def test_error_handler_classifies_responses(stream_name, ignored_code, _error_message, status_code) -> None:
    expected_action, expected_failure_type = CLASSIFICATIONS[status_code]
    if status_code == ignored_code:
        expected_action = ResponseAction.IGNORE

    resolution = _error_handler(stream_name).interpret_response(_response(status_code))

    assert resolution.response_action == expected_action
    assert resolution.failure_type == expected_failure_type


def _read_display_campaigns(child_responses):
    catalog = CatalogBuilder().with_stream("display_campaigns", SyncMode.full_refresh).build()
    with HttpMocker() as http_mocker:
        http_mocker.post(
            TOKEN_REQUEST,
            HttpResponse(body='{"access_token":"test-access-token","expires_in":3600}', status_code=200),
        )
        http_mocker.get(
            ADVERTISERS_REQUEST,
            HttpResponse(body='{"advertisers":[{"advertiser_id":123}]}', status_code=200),
        )
        http_mocker.get(CAMPAIGNS_REQUEST, child_responses)

        output = read(get_source(CONFIG), CONFIG, catalog)

    return output, http_mocker


def test_display_campaigns_ignores_404_without_errors() -> None:
    output, http_mocker = _read_display_campaigns(HttpResponse(body="{}", status_code=404))

    assert output.records == []
    assert output.errors == []
    http_mocker.assert_number_of_calls(TOKEN_REQUEST, 1)
    http_mocker.assert_number_of_calls(ADVERTISERS_REQUEST, 1)
    http_mocker.assert_number_of_calls(CAMPAIGNS_REQUEST, 1)


def test_display_campaigns_retries_server_error_then_reads_records() -> None:
    output, http_mocker = _read_display_campaigns(
        [
            HttpResponse(body="{}", status_code=500),
            HttpResponse(body=json.dumps({"results": [{"id": 456, "name": "Campaign"}]}), status_code=200),
        ]
    )

    assert len(output.records) == 1
    assert output.errors == []
    http_mocker.assert_number_of_calls(TOKEN_REQUEST, 1)
    http_mocker.assert_number_of_calls(ADVERTISERS_REQUEST, 1)
    http_mocker.assert_number_of_calls(CAMPAIGNS_REQUEST, 2)
