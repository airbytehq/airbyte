# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import logging
from pathlib import Path
from typing import Any, List, Mapping, Optional
from urllib.parse import parse_qs

import pytest
import yaml
from freezegun import freeze_time

from airbyte_cdk import ConfiguredAirbyteCatalog, SyncMode, YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"
_API = "https://miraklconnect.com/api"
_TOKEN_URL = "https://auth.mirakl.net/oauth/token"
_CLIENT_ID = "connect-client"
_CLIENT_SECRET = "connect-secret"
_ACCESS_TOKEN = "access-token-1"
_DEFAULT_START = "2020-01-01T00:00:00Z"

# name -> (path, records field, page size)
INCREMENTAL_STREAMS = {
    "orders": ("/v2/orders", "data", "100"),
    "returns": ("/v2/orders/returns", "data", "100"),
    "order_documents": ("/v2/orders/documents", "documents", "100"),
    "conversations": ("/conversations", "data", "100"),
}
FULL_REFRESH_STREAMS = {
    "products": ("/products", "data", "1000"),
}


def _config(**overrides: Any) -> Mapping[str, Any]:
    return {"client_id": _CLIENT_ID, "client_secret": _CLIENT_SECRET, **overrides}


def _catalog(stream: str, mode: SyncMode = SyncMode.full_refresh) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(stream, mode).build()


def _read(config: Mapping[str, Any], stream: str, mode: SyncMode = SyncMode.full_refresh, state: Optional[List[Any]] = None):
    catalog = _catalog(stream, mode)
    state = state if state is not None else StateBuilder().build()
    source = YamlDeclarativeSource(path_to_yaml=str(_MANIFEST_PATH), catalog=catalog, config=config, state=state)
    return entrypoint_read(source, config, catalog, state)


def _check(config: Optional[Mapping[str, Any]] = None):
    config = config or _config()
    source = YamlDeclarativeSource(path_to_yaml=str(_MANIFEST_PATH), config=config)
    return source.check(logging.getLogger("airbyte"), config)


def _mock_token(http_mocker: HttpMocker) -> None:
    http_mocker.post(
        HttpRequest(
            _TOKEN_URL,
            body=f"grant_type=client_credentials&client_id={_CLIENT_ID}&client_secret={_CLIENT_SECRET}",
        ),
        HttpResponse(json.dumps({"token_type": "Bearer", "access_token": _ACCESS_TOKEN, "expires_in": 3599})),
    )


def _request(path: str, **query: Any) -> HttpRequest:
    return HttpRequest(f"{_API}{path}", query_params=query or None, headers={"Authorization": f"Bearer {_ACCESS_TOKEN}"})


def _page(field: str, records: List[Mapping[str, Any]], next_page_token: Optional[str] = None) -> HttpResponse:
    body = {field: records}
    if next_page_token:
        body["next_page_token"] = next_page_token
    return HttpResponse(json.dumps(body))


@pytest.fixture(scope="module")
def manifest() -> Mapping[str, Any]:
    with _MANIFEST_PATH.open() as manifest_file:
        return yaml.safe_load(manifest_file)


def _stream(manifest: Mapping[str, Any], name: str) -> Mapping[str, Any]:
    return next(stream for stream in manifest["streams"] if stream["name"] == name)


def test_check_exchanges_client_credentials_and_reads_orders() -> None:
    with HttpMocker() as http_mocker:
        _mock_token(http_mocker)
        http_mocker.get(_request("/v2/orders", limit="100", updated_from=_DEFAULT_START), _page("data", [{"id": "o-1"}]))
        with freeze_time("2026-11-01T00:00:00Z"):
            status = _check()

    assert status.status.value == "SUCCEEDED", status.message


def test_check_reports_rejected_credentials_as_config_error() -> None:
    with HttpMocker() as http_mocker:
        _mock_token(http_mocker)
        http_mocker.get(
            _request("/v2/orders", limit="100", updated_from=_DEFAULT_START),
            HttpResponse(json.dumps({"status": 401, "title": "Unauthorized"}), 401),
        )
        with freeze_time("2026-11-01T00:00:00Z"):
            status = _check()

    assert status.status.value == "FAILED"
    assert "Mirakl Connect rejected the request" in status.message


@pytest.mark.parametrize("stream", sorted(INCREMENTAL_STREAMS))
def test_incremental_streams_send_updated_from_only_on_the_first_page(stream: str) -> None:
    # The seek-pagination token encodes the original filters, so follow-up pages only carry page_token.
    path, field, limit = INCREMENTAL_STREAMS[stream]
    first = [{"id": f"{stream}-1", "updated_at": "2026-10-02T00:00:00Z"}, {"id": f"{stream}-2", "updated_at": "2026-10-01T00:00:00Z"}]
    second = [{"id": f"{stream}-3", "updated_at": "2026-09-30T00:00:00Z"}]
    with HttpMocker() as http_mocker:
        _mock_token(http_mocker)
        http_mocker.get(_request(path, limit=limit, updated_from=_DEFAULT_START), _page(field, first, next_page_token="tok-2"))
        http_mocker.get(_request(path, limit=limit, page_token="tok-2"), _page(field, second))
        with freeze_time("2026-11-01T00:00:00Z"):
            output = _read(_config(), stream, SyncMode.incremental)

    assert [r.record.data["id"] for r in output.records] == [f"{stream}-1", f"{stream}-2", f"{stream}-3"]
    assert not output.errors
    assert output.most_recent_state.stream_state.__dict__["updated_at"] == "2026-10-02T00:00:00Z"


@pytest.mark.parametrize("stream", sorted(FULL_REFRESH_STREAMS))
def test_full_refresh_streams_follow_page_token(stream: str) -> None:
    path, field, limit = FULL_REFRESH_STREAMS[stream]
    with HttpMocker() as http_mocker:
        _mock_token(http_mocker)
        http_mocker.get(_request(path, limit=limit), _page(field, [{"id": "p-1"}, {"id": "p-2"}], next_page_token="tok-2"))
        http_mocker.get(_request(path, limit=limit, page_token="tok-2"), _page(field, [{"id": "p-3"}]))
        output = _read(_config(), stream)

    assert [r.record.data["id"] for r in output.records] == ["p-1", "p-2", "p-3"]
    assert not output.errors


def test_full_refresh_of_orders_still_sends_updated_from() -> None:
    # Without updated_from the orders endpoint only returns the last 30 days.
    with HttpMocker() as http_mocker:
        _mock_token(http_mocker)
        http_mocker.get(
            _request("/v2/orders", limit="100", updated_from=_DEFAULT_START),
            _page("data", [{"id": "o-1", "updated_at": "2021-03-01T00:00:00Z"}]),
        )
        with freeze_time("2026-11-01T00:00:00Z"):
            output = _read(_config(), "orders", SyncMode.full_refresh)

    assert [r.record.data["id"] for r in output.records] == ["o-1"]
    assert not output.errors


def test_start_date_is_sent_as_updated_from() -> None:
    with HttpMocker() as http_mocker:
        _mock_token(http_mocker)
        http_mocker.get(
            _request("/v2/orders/returns", limit="100", updated_from="2025-06-01T00:00:00Z"),
            _page("data", [{"id": "r-1", "updated_at": "2025-07-01T10:00:00.250Z"}]),
        )
        with freeze_time("2026-11-01T00:00:00Z"):
            output = _read(_config(start_date="2025-06-01T00:00:00Z"), "returns", SyncMode.incremental)

    assert [r.record.data["id"] for r in output.records] == ["r-1"]
    assert output.most_recent_state.stream_state.__dict__["updated_at"] == "2025-07-01T10:00:00Z"


def test_subsequent_sync_resumes_from_state() -> None:
    state = StateBuilder().with_stream_state("orders", {"updated_at": "2026-10-15T08:30:00Z"}).build()
    with HttpMocker() as http_mocker:
        _mock_token(http_mocker)
        http_mocker.get(
            _request("/v2/orders", limit="100", updated_from="2026-10-15T08:30:00Z"),
            _page("data", [{"id": "o-9", "updated_at": "2026-10-20T00:00:00+00:00"}]),
        )
        with freeze_time("2026-11-01T00:00:00Z"):
            output = _read(_config(), "orders", SyncMode.incremental, state=state)

    assert [r.record.data["id"] for r in output.records] == ["o-9"]
    assert output.most_recent_state.stream_state.__dict__["updated_at"] == "2026-10-20T00:00:00Z"


def test_access_token_is_requested_once_per_sync() -> None:
    with HttpMocker() as http_mocker:
        _mock_token(http_mocker)
        http_mocker.get(_request("/products", limit="1000"), _page("data", [{"id": "p-1"}], next_page_token="tok-2"))
        http_mocker.get(_request("/products", limit="1000", page_token="tok-2"), _page("data", [{"id": "p-2"}]))
        output = _read(_config(), "products")
        token_calls = [
            call
            for call in http_mocker._mocker.request_history  # type: ignore[attr-defined]
            if call.url == _TOKEN_URL
        ]

    assert len(output.records) == 2
    assert len(token_calls) == 1
    assert parse_qs(token_calls[0].text) == {
        "grant_type": ["client_credentials"],
        "client_id": [_CLIENT_ID],
        "client_secret": [_CLIENT_SECRET],
    }


def test_rate_limited_request_is_retried(mocker) -> None:
    mocker.patch("time.sleep", lambda _: None)
    with HttpMocker() as http_mocker:
        _mock_token(http_mocker)
        http_mocker.get(
            _request("/products", limit="1000"),
            [
                HttpResponse(json.dumps({"status": 429, "title": "Too Many Requests"}), 429),
                _page("data", [{"id": "p-1"}]),
            ],
        )
        output = _read(_config(), "products")

    assert [r.record.data["id"] for r in output.records] == ["p-1"]


def test_missing_scope_fails_with_actionable_message() -> None:
    with HttpMocker() as http_mocker:
        _mock_token(http_mocker)
        http_mocker.get(
            _request("/conversations", limit="100", updated_from=_DEFAULT_START),
            HttpResponse(json.dumps({"status": 403, "title": "Forbidden"}), 403),
        )
        with freeze_time("2026-11-01T00:00:00Z"):
            output = _read(_config(), "conversations", SyncMode.incremental)

    assert output.errors
    assert any("scope for this stream" in str(error.trace.error.message) for error in output.errors)


def test_incremental_streams_declare_cursor(manifest: Mapping[str, Any]) -> None:
    for name, (path, field, _) in INCREMENTAL_STREAMS.items():
        stream = _stream(manifest, name)
        assert stream["incremental_sync"] == {"$ref": "#/definitions/updated_at_cursor"}, name
        assert stream["retriever"]["requester"]["url"] == _API + path
        assert stream["retriever"]["record_selector"]["extractor"]["field_path"] == [field]
        assert stream["schema_loader"]["schema"]["properties"]["updated_at"]["format"] == "date-time", name
    for name in FULL_REFRESH_STREAMS:
        assert "incremental_sync" not in _stream(manifest, name)


def test_every_stream_has_id_primary_key(manifest: Mapping[str, Any]) -> None:
    for stream in manifest["streams"]:
        assert stream["primary_key"] == ["id"], stream["name"]
        assert "id" in stream["schema_loader"]["schema"]["properties"], stream["name"]


def test_client_secret_is_marked_secret(manifest: Mapping[str, Any]) -> None:
    properties = manifest["spec"]["connection_specification"]["properties"]
    assert properties["client_secret"]["airbyte_secret"] is True
    assert manifest["spec"]["connection_specification"]["required"] == ["client_id", "client_secret"]
