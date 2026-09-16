# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from pathlib import Path

import yaml


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
        assert error_handler["type"] == "CompositeErrorHandler"

        default_handler = next(handler for handler in error_handler["error_handlers"] if handler["type"] == "DefaultErrorHandler")
        backoff_strategies = default_handler["backoff_strategies"]
        assert backoff_strategies[0]["type"] == "WaitTimeFromHeader"
        assert backoff_strategies[0]["header"] == "Retry-After"
