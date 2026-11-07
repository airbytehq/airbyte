# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path
from typing import Any

import pytest
import requests
import yaml

from airbyte_cdk.sources.declarative.models.declarative_component_schema import DefaultErrorHandler as DefaultErrorHandlerModel
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.default_error_mapping import DEFAULT_ERROR_MAPPING
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction


STREAM_NAMES = ("addons", "coupons", "refunds", "licenses", "products", "transactions", "payment_methods", "addon_list_category")


@pytest.fixture(scope="module")
def manifest() -> dict[str, Any]:
    return yaml.safe_load((Path(__file__).parents[1] / "manifest.yaml").read_text())


@pytest.fixture(params=STREAM_NAMES)
def stream_name(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest.fixture
def handler_definition(stream_name: str, manifest: dict[str, Any]) -> dict[str, Any]:
    return manifest["definitions"]["streams"][stream_name]["retriever"]["requester"]["error_handler"]


def test_single_handler_preserves_response_filter(handler_definition: dict[str, Any], stream_name: str) -> None:
    response_filter = {"type": "HttpResponseFilter", "action": "IGNORE", "http_codes": [400]}
    if stream_name == "refunds":
        response_filter.update(
            predicate="{{ response.message== 'No transaction found'}}", http_codes=[], error_message="No transaction found"
        )
    assert handler_definition == {"type": "DefaultErrorHandler", "response_filters": [response_filter]}


@pytest.mark.parametrize("status_code", [200, 400, 401, 403, 404, 429, 500, 503])
@pytest.mark.parametrize("message", ["Other response", "No transaction found"])
def test_response_classification_and_retry_defaults(
    handler_definition: dict[str, Any], stream_name: str, status_code: int, message: str
) -> None:
    handler: DefaultErrorHandler = ModelToComponentFactory().create_component(DefaultErrorHandlerModel, handler_definition, config={})
    response = requests.Response()
    response.status_code = status_code
    response._content = json.dumps({"message": message}).encode()
    response.headers["Content-Type"] = "application/json"

    resolution = handler.interpret_response(response)
    ignored = (message == "No transaction found") if stream_name == "refunds" else status_code == 400
    if ignored:
        assert resolution.response_action == ResponseAction.IGNORE
        assert resolution.error_message == (
            "No transaction found" if stream_name == "refunds" else DEFAULT_ERROR_MAPPING[400].error_message
        )
    elif status_code == 200:
        assert resolution.response_action == ResponseAction.SUCCESS
    else:
        assert resolution == DEFAULT_ERROR_MAPPING[status_code]

    assert handler.max_retries == 5
    assert handler.max_time == 600
    assert not handler.backoff_strategies
    assert handler.backoff_time(response, attempt_count=0) is None
