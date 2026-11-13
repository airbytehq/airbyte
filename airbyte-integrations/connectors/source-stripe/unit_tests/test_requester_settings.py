#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from unittest.mock import patch

from conftest import get_source
from integration.config import ConfigBuilder

from airbyte_cdk.sources.streams.http.http_client import HttpClient
from airbyte_cdk.sources.streams.http.tcp_keepalive import TcpKeepaliveHTTPAdapter
from airbyte_cdk.test.state_builder import StateBuilder


def _walk_http_requesters(node: Any) -> List[Dict[str, Any]]:
    requesters: List[Dict[str, Any]] = []
    if isinstance(node, dict):
        if node.get("type") == "HttpRequester":
            requesters.append(node)
        for value in node.values():
            requesters.extend(_walk_http_requesters(value))
    elif isinstance(node, (list, tuple)):
        for value in node:
            requesters.extend(_walk_http_requesters(value))
    return requesters


def test_every_http_requester_opts_in() -> None:
    source = get_source(ConfigBuilder().build())
    requesters = _walk_http_requesters(source.resolved_manifest)
    assert requesters
    for requester in requesters:
        assert requester["use_tcp_keepalive"] is True
        assert requester["connect_timeout_in_seconds"] == 30
        assert requester["read_timeout_in_seconds"] == 80


def _build_streams_with_client_spy(config: Dict[str, Any], state=None):
    clients: List[HttpClient] = []
    original_init = HttpClient.__init__

    def spy_init(self, *args, **kwargs):
        clients.append(self)
        original_init(self, *args, **kwargs)

    with patch.object(HttpClient, "__init__", spy_init):
        streams = {stream.name: stream for stream in get_source(config, state=state).streams(config)}
    return streams, clients


def test_built_http_clients_use_settings() -> None:
    config = ConfigBuilder().build()

    streams, clients = _build_streams_with_client_spy(config)
    assert clients
    for client in clients:
        assert client._request_timeout == (30, 80)
        assert isinstance(client._session.get_adapter("https://api.stripe.com"), TcpKeepaliveHTTPAdapter)

    recent_cursor = int(datetime.now(tz=timezone.utc).timestamp()) - 3600
    state = (
        StateBuilder()
        .with_stream_state("customers", {"updated": recent_cursor})
        .with_stream_state("invoices", {"updated": recent_cursor})
        .build()
    )
    stateful_streams, stateful_clients = _build_streams_with_client_spy(config, state=state)
    assert stateful_clients

    customers_retriever = stateful_streams["customers"]._stream_partition_generator._partition_factory._retriever
    assert str(customers_retriever.requester.path) == "events"
    events_path_client = customers_retriever.requester._http_client
    assert events_path_client in stateful_clients
    assert events_path_client._request_timeout == (30, 80)
    assert isinstance(events_path_client._session.get_adapter("https://api.stripe.com"), TcpKeepaliveHTTPAdapter)
