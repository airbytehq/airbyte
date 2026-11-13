# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import logging
from pathlib import Path
from typing import Any, List, Mapping, Optional

import pytest
from freezegun import freeze_time

from airbyte_cdk import ConfiguredAirbyteCatalog, SyncMode, YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"
_PROD = "https://api.checkout.com"
_SANDBOX_PREFIXED = "https://abc123.api.sandbox.checkout.com"
_SECRET = "sk_sbox_test"
_HEADERS = {"Authorization": f"Bearer {_SECRET}"}
_START = "2026-01-01T00:00:00Z"
_NOW = "2026-01-10T00:00:00Z"


def _config(**overrides: Any) -> Mapping[str, Any]:
    return {"credentials": {"auth_type": "secret_key", "secret_key": _SECRET}, "start_date": _START, **overrides}


def _read(
    config: Mapping[str, Any],
    stream: str,
    mode: SyncMode = SyncMode.full_refresh,
    state: Optional[List[Any]] = None,
    expecting_exception: bool = False,
):
    catalog: ConfiguredAirbyteCatalog = CatalogBuilder().with_stream(stream, mode).build()
    state = state if state is not None else StateBuilder().build()
    source = YamlDeclarativeSource(path_to_yaml=str(_MANIFEST_PATH), catalog=catalog, config=config, state=state)
    return entrypoint_read(source, config, catalog, state, expecting_exception=expecting_exception)


def _check(config: Mapping[str, Any]):
    source = YamlDeclarativeSource(path_to_yaml=str(_MANIFEST_PATH), config=config)
    return source.check(logging.getLogger("airbyte"), config)


def _disputes_request(base: str = _PROD, headers: Mapping[str, str] = _HEADERS, **query: Any) -> HttpRequest:
    params = {"limit": "250", "from": _START, "to": _NOW, **query}
    return HttpRequest(f"{base}/disputes", query_params=params, headers=headers)


def _search_request(start: str, end: str, query: str = "amount:>=0") -> HttpRequest:
    return HttpRequest(f"{_PROD}/payments/search", headers=_HEADERS, body={"query": query, "limit": 1000, "from": start, "to": end})


def _payment(payment_id: str, requested_on: str) -> Mapping[str, Any]:
    return {"id": payment_id, "requested_on": requested_on, "amount": 1000, "currency": "GBP", "status": "Captured"}


@freeze_time(_NOW)
def test_check_with_secret_key_reads_disputes() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(_disputes_request(), HttpResponse(json.dumps({"total_count": 0, "data": []})))
        status = _check(_config())

    assert status.status.value == "SUCCEEDED"


@freeze_time(_NOW)
def test_check_reports_rejected_credentials_as_config_error() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(_disputes_request(), HttpResponse("", 401))
        status = _check(_config())

    assert status.status.value == "FAILED"
    assert "Checkout.com rejected the credentials" in status.message


@freeze_time(_NOW)
def test_oauth_mints_token_on_prefixed_sandbox_hosts() -> None:
    config = _config(
        credentials={"auth_type": "oauth", "client_id": "ack_test", "client_secret": "shh"},
        environment="sandbox",
        account_prefix="abc123",
    )
    with HttpMocker() as http_mocker:
        http_mocker.post(
            HttpRequest(
                "https://abc123.access.sandbox.checkout.com/connect/token",
                body="grant_type=client_credentials&client_id=ack_test&client_secret=shh",
            ),
            HttpResponse(json.dumps({"access_token": "jwt-token", "expires_in": 3600, "token_type": "Bearer"})),
        )
        http_mocker.get(
            _disputes_request(base=_SANDBOX_PREFIXED, headers={"Authorization": "Bearer jwt-token"}),
            HttpResponse(json.dumps({"total_count": 1, "data": [{"id": "dsp_1", "last_update": "2026-01-02T00:00:00Z"}]})),
        )
        output = _read(config, "disputes")

    assert [record.record.data["id"] for record in output.records] == ["dsp_1"]


@freeze_time(_NOW)
def test_disputes_paginate_with_skip_until_short_page() -> None:
    first_page = [{"id": f"dsp_{i}", "last_update": "2026-01-02T00:00:00Z"} for i in range(250)]
    with HttpMocker() as http_mocker:
        http_mocker.get(_disputes_request(), HttpResponse(json.dumps({"total_count": 251, "data": first_page})))
        http_mocker.get(
            _disputes_request(skip="250"),
            HttpResponse(json.dumps({"total_count": 251, "data": [{"id": "dsp_250", "last_update": "2026-01-03T00:00:00Z"}]})),
        )
        output = _read(_config(), "disputes")

    assert len(output.records) == 251


@freeze_time(_NOW)
def test_disputes_resume_from_state_and_normalize_cursor() -> None:
    state = StateBuilder().with_stream_state("disputes", {"last_update": "2026-01-05T00:00:00Z"}).build()
    with HttpMocker() as http_mocker:
        http_mocker.get(
            HttpRequest(f"{_PROD}/disputes", query_params={"limit": "250", "from": "2026-01-05T00:00:00Z", "to": _NOW}, headers=_HEADERS),
            HttpResponse(json.dumps({"total_count": 1, "data": [{"id": "dsp_9", "last_update": "2026-01-06T10:30:48.1234567+00:00"}]})),
        )
        output = _read(_config(), "disputes", SyncMode.incremental, state)

    assert output.records[0].record.data["last_update"] == "2026-01-06T10:30:48.123456Z"
    # State is kept at second precision, so the next sync re-reads that second and never skips a record.
    assert output.most_recent_state.stream_state.__dict__["last_update"] == "2026-01-06T10:30:48Z"


@freeze_time("2026-01-10T01:30:00Z")
def test_payments_search_walks_time_windows() -> None:
    config = _config(start_date="2026-01-10T00:00:00Z")
    with HttpMocker() as http_mocker:
        http_mocker.post(
            _search_request("2026-01-10T00:00:00Z", "2026-01-10T01:00:00Z"),
            HttpResponse(json.dumps({"data": [_payment("pay_1", "2026-01-10T00:10:00.1234567Z")]})),
        )
        http_mocker.post(
            _search_request("2026-01-10T01:00:00Z", "2026-01-10T01:30:00Z"),
            HttpResponse(json.dumps({"data": [_payment("pay_2", "2026-01-10T01:05:00Z")]})),
        )
        output = _read(config, "payments", SyncMode.incremental)

    records = {record.record.data["id"]: record.record.data for record in output.records}
    assert sorted(records) == ["pay_1", "pay_2"]
    assert records["pay_1"]["requested_on"] == "2026-01-10T00:10:00.123456Z"
    assert output.most_recent_state.stream_state.__dict__["requested_on"] == "2026-01-10T01:05:00Z"


@freeze_time("2026-01-10T00:30:00Z")
def test_payments_window_size_and_query_are_configurable() -> None:
    config = _config(start_date="2026-01-10T00:00:00Z", payments_window_minutes=15, payments_query="processing_channel_id:'pc_1'")
    with HttpMocker() as http_mocker:
        http_mocker.post(
            _search_request("2026-01-10T00:00:00Z", "2026-01-10T00:15:00Z", query="processing_channel_id:'pc_1'"),
            HttpResponse(json.dumps({"data": []})),
        )
        http_mocker.post(
            _search_request("2026-01-10T00:15:00Z", "2026-01-10T00:30:00Z", query="processing_channel_id:'pc_1'"),
            HttpResponse(json.dumps({"data": [_payment("pay_3", "2026-01-10T00:20:00Z")]})),
        )
        output = _read(config, "payments", SyncMode.incremental)

    assert [record.record.data["id"] for record in output.records] == ["pay_3"]


@freeze_time("2026-01-10T00:30:00Z")
@pytest.mark.parametrize(
    "body",
    [
        {"data": [_payment("pay_x", "2026-01-10T00:01:00Z")], "_links": {"next": {"href": f"{_PROD}/payments/search/abc?token=t"}}},
        {"data": [_payment(f"pay_{i}", "2026-01-10T00:01:00Z") for i in range(1000)]},
    ],
)
def test_payments_fail_loudly_instead_of_truncating_a_full_window(body: Mapping[str, Any]) -> None:
    config = _config(start_date="2026-01-10T00:00:00Z")
    with HttpMocker() as http_mocker:
        http_mocker.post(_search_request("2026-01-10T00:00:00Z", "2026-01-10T00:30:00Z"), HttpResponse(json.dumps(body)))
        output = _read(config, "payments", SyncMode.incremental, expecting_exception=True)

    assert output.records == []
    assert any("held more than 1,000 payments" in error.trace.error.message for error in output.errors)


@freeze_time("2026-01-10T00:30:00Z")
def test_payment_actions_are_read_per_payment_with_payment_id() -> None:
    config = _config(start_date="2026-01-10T00:00:00Z")
    with HttpMocker() as http_mocker:
        http_mocker.post(
            _search_request("2026-01-10T00:00:00Z", "2026-01-10T00:30:00Z"),
            HttpResponse(json.dumps({"data": [_payment("pay_1", "2026-01-10T00:01:00Z"), _payment("pay_2", "2026-01-10T00:02:00Z")]})),
        )
        http_mocker.get(
            HttpRequest(f"{_PROD}/payments/pay_1/actions", headers=_HEADERS),
            HttpResponse(json.dumps([{"id": "act_1", "type": "Authorization"}, {"id": "act_2", "type": "Capture"}])),
        )
        http_mocker.get(
            HttpRequest(f"{_PROD}/payments/pay_2/actions", headers=_HEADERS),
            HttpResponse(json.dumps([{"id": "act_3", "type": "Refund"}])),
        )
        output = _read(config, "payment_actions")

    assert sorted((r.record.data["id"], r.record.data["payment_id"]) for r in output.records) == [
        ("act_1", "pay_1"),
        ("act_2", "pay_1"),
        ("act_3", "pay_2"),
    ]


@freeze_time("2026-01-10T00:30:00Z")
def test_financial_actions_follow_pagination_token() -> None:
    config = _config(start_date="2026-01-10T00:00:00Z")
    next_href = f"{_PROD}/financial-actions?payment_id=pay_1&limit=100&pagination_token=tok2"
    with HttpMocker() as http_mocker:
        http_mocker.post(
            _search_request("2026-01-10T00:00:00Z", "2026-01-10T00:30:00Z"),
            HttpResponse(json.dumps({"data": [_payment("pay_1", "2026-01-10T00:01:00Z")]})),
        )
        http_mocker.get(
            HttpRequest(f"{_PROD}/financial-actions", query_params={"payment_id": "pay_1", "limit": "100"}, headers=_HEADERS),
            HttpResponse(
                json.dumps({"count": 1, "data": [{"payment_id": "pay_1", "action_id": "act_1"}], "_links": {"next": {"href": next_href}}})
            ),
        )
        http_mocker.get(
            HttpRequest(
                f"{_PROD}/financial-actions",
                query_params={"payment_id": "pay_1", "limit": "100", "pagination_token": "tok2"},
                headers=_HEADERS,
            ),
            HttpResponse(json.dumps({"count": 1, "data": [{"payment_id": "pay_1", "action_id": "act_2"}], "_links": {}})),
        )
        output = _read(config, "financial_actions")

    assert [r.record.data["action_id"] for r in output.records] == ["act_1", "act_2"]


@freeze_time(_NOW)
def test_reports_filter_by_created_date_and_paginate() -> None:
    base_query = {"limit": "100", "created_after": _START, "created_before": _NOW}
    with HttpMocker() as http_mocker:
        http_mocker.get(
            HttpRequest(f"{_PROD}/reports", query_params=base_query, headers=_HEADERS),
            HttpResponse(
                json.dumps(
                    {
                        "count": 1,
                        "data": [{"id": "rpt_1", "created_on": "2026-01-02T00:00:00Z"}],
                        "_links": {"next": {"href": f"{_PROD}/reports?limit=100&pagination_token=p2"}},
                    }
                )
            ),
        )
        http_mocker.get(
            HttpRequest(f"{_PROD}/reports", query_params={**base_query, "pagination_token": "p2"}, headers=_HEADERS),
            HttpResponse(
                json.dumps({"count": 1, "data": [{"id": "rpt_2", "created_on": "2026-01-03T09:00:00.7250000+00:00"}], "_links": {}})
            ),
        )
        output = _read(_config(), "reports", SyncMode.incremental)

    assert [r.record.data["id"] for r in output.records] == ["rpt_1", "rpt_2"]
    assert output.most_recent_state.stream_state.__dict__["created_on"] == "2026-01-03T09:00:00Z"


@freeze_time(_NOW)
def test_workflows_full_refresh() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(
            HttpRequest(f"{_PROD}/workflows", headers=_HEADERS),
            HttpResponse(json.dumps({"data": [{"id": "wf_1", "name": "Webhooks", "active": True}]})),
        )
        output = _read(_config(), "workflows")

    assert output.records[0].record.data["name"] == "Webhooks"


@freeze_time(_NOW)
def test_rate_limits_are_retried(mocker) -> None:
    mocker.patch("time.sleep", lambda _: None)
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _disputes_request(),
            [
                HttpResponse("", 429),
                HttpResponse(json.dumps({"total_count": 1, "data": [{"id": "dsp_1", "last_update": "2026-01-02T00:00:00Z"}]})),
            ],
        )
        output = _read(_config(), "disputes")

    assert len(output.records) == 1
