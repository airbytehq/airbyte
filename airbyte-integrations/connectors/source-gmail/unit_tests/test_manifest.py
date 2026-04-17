#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#
"""Tests that validate the declarative manifest changes introduced for audit
recommendations: incremental sync on `messages`, substream `incremental_dependency`,
top-level `concurrency_level`, top-level `api_budget`, and Gmail-specific
rate-limit handling via a Retry-After-aware error handler.
"""

from typing import Any, Mapping


def _streams_by_name(manifest: Mapping[str, Any]) -> Mapping[str, Any]:
    return manifest["definitions"]["streams"]


def test_top_level_concurrency_level_is_configured(manifest):
    """The manifest must declare a top-level ConcurrencyLevel so substream
    fan-out (messages_details, threads_details) can be parallelized."""
    concurrency = manifest.get("concurrency_level")
    assert concurrency is not None, "Expected top-level concurrency_level block"
    assert concurrency["type"] == "ConcurrencyLevel"
    assert concurrency.get("max_concurrency", 0) >= 1
    assert "default_concurrency" in concurrency


def test_top_level_api_budget_is_configured_for_gmail_quota(manifest):
    """The manifest must declare an HTTPAPIBudget with a moving-window call-rate
    policy so the connector proactively respects Gmail's per-user quota."""
    api_budget = manifest.get("api_budget")
    assert api_budget is not None, "Expected top-level api_budget block"
    assert api_budget["type"] == "HTTPAPIBudget"

    policies = api_budget.get("policies") or []
    assert policies, "Expected at least one rate-limit policy"
    assert any(p.get("type") == "MovingWindowCallRatePolicy" for p in policies)

    # 429 must be treated as a rate-limit hit so the budget backs off.
    rate_limit_codes = api_budget.get("status_codes_for_ratelimit_hit") or []
    assert 429 in rate_limit_codes


def test_base_requester_has_retry_after_error_handler(manifest):
    """The base HttpRequester must honour Gmail's Retry-After header on 429s."""
    base_requester = manifest["definitions"]["base_requester"]
    error_handler = base_requester.get("error_handler")
    assert error_handler is not None, "base_requester must define an error_handler"

    # Flatten nested handlers to look for WaitTimeFromHeader on 429.
    handlers = error_handler.get("error_handlers", [error_handler])
    found_retry_after = False
    for handler in handlers:
        for strategy in handler.get("backoff_strategies", []) or []:
            if strategy.get("type") == "WaitTimeFromHeader" and strategy.get("header") == "Retry-After":
                found_retry_after = True
    assert found_retry_after, "Expected a WaitTimeFromHeader backoff for Retry-After"


def test_messages_stream_has_datetime_incremental_cursor(manifest):
    """`messages` must sync incrementally using the Gmail `internalDate` cursor."""
    messages = _streams_by_name(manifest)["messages"]
    incremental = messages.get("incremental_sync")
    assert incremental is not None, "messages stream must declare incremental_sync"
    assert incremental["type"] == "DatetimeBasedCursor"
    assert incremental["cursor_field"] == "internalDate"
    # Cursor is stored as a unix-second epoch for Gmail `q=after:<ts>` injection.
    assert incremental["datetime_format"] == "%s"
    assert "%ms" in incremental["cursor_datetime_formats"]


def test_messages_stream_injects_after_query_parameter(manifest):
    """`messages` must pass the cursor into the Gmail `q=after:<ts>` parameter
    so the server-side filter matches the client-side cursor."""
    messages = _streams_by_name(manifest)["messages"]
    params = messages["retriever"]["requester"]["request_parameters"]
    assert "q" in params, "messages retriever must inject a Gmail `q` parameter"
    assert "after:" in params["q"]
    assert "stream_interval.start_time" in params["q"]


def test_messages_details_depends_on_parent_cursor(manifest):
    """`messages_details` must rely on `messages` incremental state so we only
    fetch details for new/changed messages on subsequent syncs."""
    details = _streams_by_name(manifest)["messages_details"]
    parent_configs = details["retriever"]["partition_router"]["parent_stream_configs"]
    assert parent_configs, "messages_details must declare parent_stream_configs"
    assert parent_configs[0].get("incremental_dependency") is True


def test_threads_and_drafts_apply_start_date_filter(manifest):
    """`threads` and `drafts` cannot use a datetime cursor (their list responses
    do not expose `internalDate`) but must still honour `start_date` via the
    Gmail server-side `q=after:` filter when the user sets one."""
    streams = _streams_by_name(manifest)
    for name in ("threads", "drafts"):
        params = streams[name]["retriever"]["requester"]["request_parameters"]
        assert "q" in params, f"{name} retriever must inject a Gmail `q` parameter"
        assert "start_date" in params["q"]
        assert "after:" in params["q"]


def test_spec_exposes_optional_start_date(manifest):
    """The spec must expose an optional `start_date` config field (non-breaking)."""
    props = manifest["spec"]["connection_specification"]["properties"]
    assert "start_date" in props
    # Not required — backward-compatible with existing configs.
    required = manifest["spec"]["connection_specification"].get("required", [])
    assert "start_date" not in required
