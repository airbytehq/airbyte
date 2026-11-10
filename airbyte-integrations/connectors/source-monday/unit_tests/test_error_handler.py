# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
import requests
import yaml

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    CompositeErrorHandler as CompositeErrorHandlerModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DefaultErrorHandler as DefaultErrorHandlerModel
from airbyte_cdk.sources.declarative.parsers.manifest_component_transformer import ManifestComponentTransformer
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction


MANIFEST_PATH = Path(__file__).resolve().parent.parent / "manifest.yaml"


def _resolved_manifest() -> dict[str, Any]:
    return ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(MANIFEST_PATH.read_text()))


def _error_handler_definition() -> dict[str, Any]:
    manifest = _resolved_manifest()
    return ManifestComponentTransformer().propagate_types_and_parameters("", manifest["definitions"]["requester"]["error_handler"], {})


def _build_error_handler() -> Any:
    definition = _error_handler_definition()
    model_class = CompositeErrorHandlerModel if definition["type"] == "CompositeErrorHandler" else DefaultErrorHandlerModel
    model = model_class.parse_obj(definition)
    return ModelToComponentFactory().create_component(type(model), definition, config={})


def _walk(node: Any) -> Iterator[Any]:
    yield node
    if isinstance(node, dict):
        for value in node.values():
            yield from _walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk(value)


def _graphql_error(code: str) -> dict[str, Any]:
    return {"data": None, "errors": [{"message": f"Error {code}", "extensions": {"code": code}}]}


def _response(status_code: int, body: dict[str, Any], headers: dict[str, str] | None = None) -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    response._content = json.dumps(body).encode()
    response.headers["Content-Type"] = "application/json"
    if headers:
        response.headers.update(headers)
    return response


def test_manifest_has_no_composite_error_handler() -> None:
    manifest = _resolved_manifest()

    assert not any(isinstance(node, dict) and node.get("type") == "CompositeErrorHandler" for node in _walk(manifest))


def test_manifest_keeps_the_http_403_skip_filter() -> None:
    manifest = _resolved_manifest()
    handler_definition = manifest["definitions"]["requester"]["error_handler"]
    filters = [
        response_filter
        for node in _walk(handler_definition)
        if isinstance(node, dict)
        for response_filter in node.get("response_filters", [])
    ]

    assert {"http_codes": [403], "action": "IGNORE"} in filters


@pytest.mark.parametrize(
    ("status_code", "body", "expected_action", "expected_failure_type"),
    [
        (200, _graphql_error("COMPLEXITY_BUDGET_EXHAUSTED"), ResponseAction.RETRY, FailureType.system_error),
        (429, _graphql_error("COMPLEXITY_BUDGET_EXHAUSTED"), ResponseAction.RETRY, FailureType.transient_error),
        (200, _graphql_error("CursorExpiredError"), ResponseAction.RESET_PAGINATION, FailureType.system_error),
        (200, _graphql_error("FIELD_LIMIT_EXCEEDED"), ResponseAction.RETRY, FailureType.system_error),
        (403, {"message": "Forbidden"}, ResponseAction.IGNORE, None),
        (403, _graphql_error("InvalidArgumentException"), ResponseAction.IGNORE, None),
        (403, _graphql_error("COMPLEXITY_BUDGET_EXHAUSTED"), ResponseAction.RETRY, FailureType.config_error),
        (200, _graphql_error("InvalidArgumentException"), ResponseAction.SUCCESS, None),
        (
            200,
            {
                "data": {"me": {"id": "1"}},
                "errors": [{"message": "Photo unavailable.", "extensions": {"code": "ASSET_UNAVAILABLE"}}],
            },
            ResponseAction.SUCCESS,
            None,
        ),
        (500, {}, ResponseAction.RETRY, FailureType.transient_error),
        (502, {}, ResponseAction.RETRY, FailureType.transient_error),
        (429, {}, ResponseAction.RATE_LIMITED, FailureType.transient_error),
        (401, {}, ResponseAction.FAIL, FailureType.config_error),
        (400, {}, ResponseAction.FAIL, FailureType.system_error),
    ],
)
def test_interpret_response(
    status_code: int,
    body: dict[str, Any],
    expected_action: ResponseAction,
    expected_failure_type: FailureType | None,
) -> None:
    result = _build_error_handler().interpret_response(_response(status_code, body))

    assert result.response_action == expected_action
    if expected_failure_type is not None:
        assert result.failure_type == expected_failure_type


def test_backoff_strategy_order_and_max_retries() -> None:
    handler = _build_error_handler()

    def first_backoff(response: requests.Response) -> float | None:
        return next(
            (value for strategy in handler.backoff_strategies if (value := strategy.backoff_time(response, 1)) is not None),
            None,
        )

    assert first_backoff(_response(429, {}, {"retry-after": "7"})) == 7
    assert first_backoff(_response(429, {})) == 60
    assert handler.max_retries == 5
