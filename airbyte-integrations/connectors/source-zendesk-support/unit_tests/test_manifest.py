# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""Manifest-level assertions that do not require mocking HTTP calls."""

import copy
from datetime import timedelta

from airbyte_cdk.sources.declarative.concurrent_declarative_source import ConcurrentDeclarativeSource
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .conftest import get_source
from .mock_server.config import ConfigBuilder


_NOW = ab_datetime_now()
_START_DATE = _NOW.subtract(timedelta(weeks=104))


def _config():
    return (
        ConfigBuilder()
        .with_basic_auth_credentials("user@example.com", "password")
        .with_subdomain("d3v-airbyte")
        .with_start_date(_START_DATE)
        .build()
    )


def _resolved_stream_configs():
    source = get_source(config=_config())
    resolved = source.resolved_manifest
    return {stream["name"]: stream for stream in resolved["streams"]}


def _parent_ticket_configs(streams):
    """Collect every embedded copy of the tickets stream used as a substream parent."""
    parents = []

    def collect(partition_router):
        if isinstance(partition_router, dict) and partition_router.get("parent_stream_configs"):
            for parent_config in partition_router["parent_stream_configs"]:
                if parent_config["stream"]["name"] == "tickets":
                    parents.append(parent_config["stream"])
        elif isinstance(partition_router, list):
            for router in partition_router:
                collect(router)

    for stream in streams.values():
        if stream.get("type") == "StateDelegatingStream":
            for variant in ("full_refresh_stream", "incremental_stream"):
                if variant in stream:
                    collect(stream[variant].get("retriever", {}).get("partition_router"))
        collect(stream.get("retriever", {}).get("partition_router"))
    return parents


def test_tickets_stream_disables_response_cache():
    """`tickets` pages can be ~160 MB; caching each to SQLite adds memory pressure, so the
    stream opts out -- and so do the embedded parent copies walked by `side_conversations`
    and the stateful `ticket_metrics` stream."""
    streams = _resolved_stream_configs()

    tickets = streams["tickets"]
    assert tickets["retriever"]["requester"]["use_cache"] is False

    # `side_conversations` and the stateful `ticket_metrics` path each embed a parent copy of
    # `tickets_stream`; all of them inherit the cache opt-out.
    parents = _parent_ticket_configs(streams)
    assert parents, "expected at least one parent stream config referencing tickets"
    for parent in parents:
        assert parent["retriever"]["requester"]["use_cache"] is False

    # Sanity check on scope: the opt-out is deliberate on tickets only, other streams keep the default.
    users = streams["users"]
    assert users["retriever"]["requester"].get("use_cache") is not False


def test_cache_initialization_keeps_tickets_uncached():
    """ConcurrentDeclarativeSource._initialize_cache_for_parent_streams flips parent requesters to
    `use_cache: true` unless the stream explicitly sets `use_cache: false`; the tickets stream must
    survive that pass unchanged."""
    streams = _resolved_stream_configs()
    stream_configs = [copy.deepcopy(s) for s in streams.values()]

    initialized = ConcurrentDeclarativeSource._initialize_cache_for_parent_streams(stream_configs)

    for stream_config in initialized:
        if stream_config["name"] == "tickets":
            assert stream_config["retriever"]["requester"]["use_cache"] is False
        if stream_config["name"] == "side_conversations":
            parent = stream_config["retriever"]["partition_router"]["parent_stream_configs"][0]["stream"]
            assert parent["retriever"]["requester"]["use_cache"] is False
