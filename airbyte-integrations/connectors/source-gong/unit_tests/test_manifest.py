# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from pathlib import Path

import yaml
from _helpers import get_source


def test_manifest_honors_retry_after_on_rate_limit():
    manifest_path = Path(__file__).parent.parent / "manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text())

    assert "response_filters" not in manifest["definitions"]

    api_budget = manifest["api_budget"]
    assert api_budget["type"] == "HTTPAPIBudget"
    policy = api_budget["policies"][0]
    assert policy["type"] == "MovingWindowCallRatePolicy"
    assert policy["rates"][0]["limit"] == 3
    assert policy["rates"][0]["interval"] == "PT1S"
    assert policy["matchers"] == []

    streams = manifest["definitions"]["streams"]
    for stream_name, stream in streams.items():
        error_handler = stream["retriever"]["requester"]["error_handler"]
        assert error_handler["type"] == "DefaultErrorHandler", stream_name

        backoff_strategies = error_handler["backoff_strategies"]
        assert backoff_strategies[0]["type"] == "WaitTimeFromHeader"
        assert backoff_strategies[0]["header"] == "Retry-After"


_CONFIG = {
    "credentials": {
        "auth_type": "APIKey",
        "access_key": "test_access_key",
        "access_key_secret": "test_access_key_secret",
    },
    "start_date": "2024-01-01T00:00:00Z",
}


def _error_handlers(node):
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "error_handler":
                yield value
            yield from _error_handlers(value)
    elif isinstance(node, list):
        for item in node:
            yield from _error_handlers(item)


def test_every_stream_uses_a_single_default_error_handler():
    resolved_manifest = get_source(_CONFIG).resolved_manifest

    error_handler_types = {error_handler["type"] for error_handler in _error_handlers(resolved_manifest)}
    assert error_handler_types == {"DefaultErrorHandler"}

    for stream in resolved_manifest["streams"]:
        error_handler = stream["retriever"]["requester"]["error_handler"]
        assert error_handler["type"] == "DefaultErrorHandler", stream["name"]
        filter_actions = [response_filter.get("action") for response_filter in error_handler["response_filters"]]
        assert filter_actions == ["IGNORE", "FAIL", "RATE_LIMITED", "RETRY"], stream["name"]
