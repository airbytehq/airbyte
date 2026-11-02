# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
import requests
import yaml

from airbyte_cdk.sources.declarative.models import DefaultErrorHandler as DefaultErrorHandlerModel
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction


MANIFEST_PATH = Path(__file__).parents[1] / "manifest.yaml"
MANIFEST = yaml.safe_load(MANIFEST_PATH.read_text())
EXPECTED_FILTERS = {
    "conversations": ([403], None, "App only access is restricting some resources"),
    "channels": ([404], "No threadId found for TeamId", "Resource not found for team Ids"),
    "channel_members": ([404], "No Team found with Group id", "Resource not found for group Ids"),
    "channel_tabs": ([404], "No Team found with Group id", "Resource not found for group Ids"),
    "conversation_threads": ([404, 403], "App Only access is not allowed", "Some resources not found for parent resources"),
    "conversation_posts": ([404, 403, 503], "App Only access is not allowed", "Some resources are not allowed to extract"),
    "team_drives": ([404, 403], None, "Some resources are not found or not allowed to access"),
    "team_device_usage_report": ([400], None, "Personal account not supported"),
}


def error_handlers(node: Any, stream_names: tuple[str, ...] = ()) -> Iterator[tuple[tuple[str, ...], dict[str, Any]]]:
    if isinstance(node, dict):
        if node.get("type") == "DeclarativeStream":
            stream_names += (node["name"],)
        for key, value in node.items():
            if key == "error_handler":
                yield stream_names, value
            else:
                yield from error_handlers(value, stream_names)
    elif isinstance(node, list):
        for value in node:
            yield from error_handlers(value, stream_names)


HANDLERS = list(error_handlers(MANIFEST))


def test_all_error_handlers_are_covered() -> None:
    assert len(HANDLERS) == 14
    assert {names[-1] for names, _ in HANDLERS} == set(EXPECTED_FILTERS)


@pytest.mark.parametrize("stream_names,definition", HANDLERS, ids=["/".join(names) for names, _ in HANDLERS])
def test_direct_error_handler_preserves_filters_and_resolutions(stream_names: tuple[str, ...], definition: dict[str, Any]) -> None:
    codes, predicate, message = EXPECTED_FILTERS[stream_names[-1]]
    expected_filter = {"type": "HttpResponseFilter", "action": "IGNORE", "http_codes": codes, "error_message": message}
    if predicate:
        expected_filter["predicate"] = f"{{{{ '{predicate}' in response }}}}"
    assert definition == {"type": "DefaultErrorHandler", "response_filters": [expected_filter]}

    handler = ModelToComponentFactory().create_component(DefaultErrorHandlerModel, definition, config={})
    assert isinstance(handler, DefaultErrorHandler)
    assert handler.max_retries == 5
    assert handler.max_time == 600
    assert not handler.backoff_strategies

    fallback = DefaultErrorHandler(config={}, parameters={})
    for status in (200, 400, 401, 403, 404, 418, 429, 500, 503):
        for body in ({"error": {"message": "Unrelated error"}}, {predicate: "present"} if predicate else {}):
            response = requests.Response()
            response.status_code = status
            response._content = json.dumps(body).encode()
            response.request = requests.Request("GET", "https://graph.microsoft.com/v1.0/test").prepare()
            resolution = handler.interpret_response(response)
            if status in codes or (predicate and predicate in body):
                assert resolution.response_action == ResponseAction.IGNORE
                assert resolution.error_message == message
            else:
                assert resolution == fallback.interpret_response(response)
