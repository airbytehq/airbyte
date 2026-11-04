# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import logging
from pathlib import Path
from typing import Any, List, Mapping, Optional

import pytest
import yaml
from freezegun import freeze_time

from airbyte_cdk import ConfiguredAirbyteCatalog, SyncMode, YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"
_PROD = "https://api.rillet.com"
_SANDBOX = "https://sandbox.api.rillet.com"
_API_KEY = "rillet-test-key"
_HEADERS = {"Authorization": f"Bearer {_API_KEY}", "X-Rillet-API-Version": "4"}
_EPOCH = "1970-01-01T00:00:00Z"

INCREMENTAL_STREAMS = {
    "accounts": "/accounts",
    "customers": "/customers",
    "invoices": "/invoices",
    "invoice_payments": "/invoice-payments",
    "credit_memos": "/credit-memos",
    "vendors": "/vendors",
    "vendor_credits": "/vendor-credits",
    "bills": "/bills",
    "charges": "/charges",
    "reimbursements": "/reimbursements",
    "journal_entries": "/journal-entries",
}
PAGINATED_STREAMS = {
    "customers": ("/customers", "customers"),
    "customer_families": ("/customer-families", "customer_families"),
    "products": ("/products", "products"),
    "contracts": ("/contracts", "contracts"),
    "invoices": ("/invoices", "invoices"),
    "invoice_payments": ("/invoice-payments", "payments"),
    "credit_memos": ("/credit-memos", "credit_memos"),
    "vendors": ("/vendors", "vendors"),
    "vendor_credits": ("/vendor-credits", "vendor_credits"),
    "bills": ("/bills", "bills"),
    "charges": ("/charges", "charges"),
    "reimbursements": ("/reimbursements", "reimbursements"),
    "journal_entries": ("/journal-entries", "journal_entries"),
    "bank_transactions": ("/bank-transactions", "bank_transactions"),
    "members": ("/members", "members"),
}


def _config(**overrides: Any) -> Mapping[str, Any]:
    return {"api_key": _API_KEY, **overrides}


def _catalog(stream: str, mode: SyncMode = SyncMode.full_refresh) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(stream, mode).build()


def _read(config: Mapping[str, Any], stream: str, mode: SyncMode = SyncMode.full_refresh, state: Optional[List[Any]] = None):
    catalog = _catalog(stream, mode)
    state = state if state is not None else StateBuilder().build()
    source = YamlDeclarativeSource(path_to_yaml=str(_MANIFEST_PATH), catalog=catalog, config=config, state=state)
    return entrypoint_read(source, config, catalog, state)


def _check():
    source = YamlDeclarativeSource(path_to_yaml=str(_MANIFEST_PATH), config=_config())
    return source.check(logging.getLogger("airbyte"), _config())


def _request(path: str, base: str = _PROD, **query: Any) -> HttpRequest:
    return HttpRequest(f"{base}{path}", query_params=query or None, headers=_HEADERS)


def _page(field: str, records: List[Mapping[str, Any]], next_cursor: Optional[str] = None) -> HttpResponse:
    pagination = {"next_cursor": next_cursor} if next_cursor else {}
    return HttpResponse(json.dumps({field: records, "pagination": pagination}))


@pytest.fixture(scope="module")
def manifest() -> Mapping[str, Any]:
    with _MANIFEST_PATH.open() as manifest_file:
        return yaml.safe_load(manifest_file)


def _stream(manifest: Mapping[str, Any], name: str) -> Mapping[str, Any]:
    return next(stream for stream in manifest["streams"] if stream["name"] == name)


def test_check_reads_current_organization() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("/organizations/self"),
            HttpResponse(json.dumps({"id": "org-1", "currency": "USD", "timezone": "America/New_York", "trade_name": "Acme"})),
        )
        status = _check()

    assert status.status.value == "SUCCEEDED"


def test_check_reports_invalid_key_as_config_error() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(_request("/organizations/self"), HttpResponse(json.dumps({"status": 401, "title": "Unauthorized"}), 401))
        status = _check()

    assert status.status.value == "FAILED"
    assert "Rillet rejected the API key" in status.message


@pytest.mark.parametrize("stream,path_and_field", sorted(PAGINATED_STREAMS.items()))
def test_streams_follow_next_cursor_until_exhausted(stream: str, path_and_field: Any) -> None:
    path, field = path_and_field
    # In full refresh, incremental streams still send updated.gt with the epoch default, which returns everything.
    query = {"updated.gt": _EPOCH} if stream in INCREMENTAL_STREAMS else {}
    stamp = {"updated_at": "2026-01-01T00:00:00Z"} if stream in INCREMENTAL_STREAMS else {}
    first = [{"id": f"{stream}-1", **stamp}, {"id": f"{stream}-2", **stamp}]
    second = [{"id": f"{stream}-3", **stamp}]
    with HttpMocker() as http_mocker:
        http_mocker.get(_request(path, limit="100", **query), _page(field, first, next_cursor="abc123"))
        http_mocker.get(_request(path, limit="100", cursor="abc123", **query), _page(field, second))
        with freeze_time("2026-01-02T00:00:00Z"):
            output = _read(_config(), stream)

    assert [r.record.data["id"] for r in output.records] == [f"{stream}-1", f"{stream}-2", f"{stream}-3"]
    assert not output.errors


def test_sandbox_environment_uses_sandbox_host() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("/subsidiaries", base=_SANDBOX),
            HttpResponse(json.dumps({"subsidiaries": [{"id": "sub-1", "type": "LEGAL_ENTITY"}], "root_subsidiary_id": "sub-1"})),
        )
        output = _read(_config(environment="sandbox"), "subsidiaries")

    assert [r.record.data["id"] for r in output.records] == ["sub-1"]


def test_full_history_on_first_incremental_sync_and_state_is_max_updated_at() -> None:
    # Rillet returns newest first, so the highest updated_at is on the first page.
    first = [
        {"id": "je-3", "updated_at": "2026-03-05T10:00:00Z"},
        {"id": "je-2", "updated_at": "2026-03-04T09:30:00.123Z"},
    ]
    second = [{"id": "je-1", "updated_at": "2026-01-15T08:00:00Z"}]
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("/journal-entries", limit="100", **{"updated.gt": _EPOCH}), _page("journal_entries", first, next_cursor="n1")
        )
        http_mocker.get(_request("/journal-entries", limit="100", cursor="n1", **{"updated.gt": _EPOCH}), _page("journal_entries", second))
        with freeze_time("2026-03-06T00:00:00Z"):
            output = _read(_config(), "journal_entries", SyncMode.incremental)

    assert [r.record.data["id"] for r in output.records] == ["je-3", "je-2", "je-1"]
    final_state = output.most_recent_state.stream_state.__dict__
    assert final_state["updated_at"] == "2026-03-05T10:00:00Z"


def test_start_date_is_sent_as_updated_gt() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("/invoices", limit="100", **{"updated.gt": "2025-06-01T00:00:00Z"}),
            _page("invoices", [{"id": "inv-1", "updated_at": "2025-07-01T00:00:00Z"}]),
        )
        with freeze_time("2026-01-01T00:00:00Z"):
            output = _read(_config(start_date="2025-06-01T00:00:00Z"), "invoices", SyncMode.incremental)

    assert [r.record.data["id"] for r in output.records] == ["inv-1"]


def test_subsequent_sync_resumes_from_state() -> None:
    state = StateBuilder().with_stream_state("bills", {"updated_at": "2026-02-01T12:30:45Z"}).build()
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("/bills", limit="100", **{"updated.gt": "2026-02-01T12:30:45Z"}),
            _page("bills", [{"id": "bill-9", "updated_at": "2026-02-03T00:00:00Z"}]),
        )
        with freeze_time("2026-02-04T00:00:00Z"):
            output = _read(_config(start_date="2020-01-01T00:00:00Z"), "bills", SyncMode.incremental, state=state)

    assert [r.record.data["id"] for r in output.records] == ["bill-9"]
    assert output.most_recent_state.stream_state.__dict__["updated_at"] == "2026-02-03T00:00:00Z"


def test_unpaginated_incremental_stream_accounts() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("/accounts", **{"updated.gt": _EPOCH}),
            HttpResponse(json.dumps({"accounts": [{"id": "acc-1", "code": "1000", "updated_at": "2026-01-01T00:00:00Z"}]})),
        )
        with freeze_time("2026-01-02T00:00:00Z"):
            output = _read(_config(), "accounts", SyncMode.incremental)

    assert [r.record.data["id"] for r in output.records] == ["acc-1"]


def test_rate_limited_request_is_retried(mocker) -> None:
    mocker.patch("time.sleep", lambda _: None)
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("/members", limit="100"),
            [
                HttpResponse(json.dumps({"status": 429, "title": "Too Many Requests"}), 429),
                _page("members", [{"id": "m-1", "email": "a@example.com"}]),
            ],
        )
        output = _read(_config(), "members")

    assert [r.record.data["id"] for r in output.records] == ["m-1"]


def test_book_periods_404_means_no_periods_not_a_failure() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(_request("/books/periods"), HttpResponse(json.dumps({"status": 404, "title": "Not Found"}), 404))
        output = _read(_config(), "book_periods")

    assert output.records == []
    assert not output.errors


def test_money_amounts_stay_strings_to_preserve_precision(manifest: Mapping[str, Any]) -> None:
    props = _stream(manifest, "invoices")["schema_loader"]["schema"]["properties"]
    amount = props["total"]["properties"]["amount"]
    assert amount["type"] == ["string", "null"]


def test_incremental_streams_declare_cursor_and_filter(manifest: Mapping[str, Any]) -> None:
    for name, path in INCREMENTAL_STREAMS.items():
        stream = _stream(manifest, name)
        assert stream["incremental_sync"] == {"$ref": "#/definitions/updated_at_cursor"}, name
        assert stream["retriever"]["requester"]["path"] == path
        assert stream["schema_loader"]["schema"]["properties"]["updated_at"]["format"] == "date-time"
    cursor = manifest["definitions"]["updated_at_cursor"]
    assert cursor["start_time_option"]["field_name"] == "updated.gt"


def test_every_stream_has_id_primary_key(manifest: Mapping[str, Any]) -> None:
    for stream in manifest["streams"]:
        assert stream["primary_key"] == ["id"], stream["name"]
        assert "id" in stream["schema_loader"]["schema"]["properties"], stream["name"]
