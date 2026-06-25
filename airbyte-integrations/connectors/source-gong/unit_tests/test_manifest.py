# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from pathlib import Path

import yaml


def test_manifest_maps_429_to_rate_limited():
    manifest_path = Path(__file__).parent.parent / "manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text())

    rate_limit = manifest["definitions"]["response_filters"]["rate_limit"]
    assert rate_limit["type"] == "HttpResponseFilter"
    assert rate_limit["action"] == "RATE_LIMITED"
    assert 429 in rate_limit["http_codes"]
    assert rate_limit["backoff_strategies"][0]["type"] == "WaitTimeFromHeader"
    assert rate_limit["backoff_strategies"][0]["header"] == "Retry-After"

    streams = manifest["definitions"]["streams"]
    for stream_name, stream in streams.items():
        error_handler = stream["retriever"]["requester"]["error_handler"]
        assert error_handler["type"] == "CompositeErrorHandler"

        default_handler = next(
            handler for handler in error_handler["error_handlers"] if handler["type"] == "DefaultErrorHandler"
        )
        response_filters = default_handler["response_filters"]
        assert any(
            filter_spec.get("$ref") == "#/definitions/response_filters/rate_limit"
            for filter_spec in response_filters
        ), f"Stream {stream_name} does not include a shared Gateway rate limit response filter"
