# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path
from typing import Any, Mapping

import pytest
import requests_mock
import yaml
from freezegun import freeze_time

from airbyte_cdk import ConfiguredAirbyteCatalog, SyncMode, YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"
_BASE = "https://sochain.com/api/v3"
_ADDRESS = "DH5yaieqoZN36fDVciNyRueRGvGLR3mr7L"
_CONFIG = {"network": "DOGE", "addresses": [_ADDRESS]}


def _catalog(stream: str, mode: SyncMode = SyncMode.full_refresh) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(stream, mode).build()


def _read(stream: str, config: Mapping[str, Any], mode: SyncMode = SyncMode.full_refresh, state=None, expecting_exception: bool = False):
    catalog = _catalog(stream, mode)
    state = state or StateBuilder().build()
    source = YamlDeclarativeSource(path_to_yaml=str(_MANIFEST_PATH), catalog=catalog, config=config, state=state)
    return entrypoint_read(source, config, catalog, state, expecting_exception=expecting_exception)


def _success(data: Mapping[str, Any]) -> str:
    return json.dumps({"status": "success", "data": data})


def _tx(tx_hash: str, time: int) -> Mapping[str, Any]:
    return {
        "hash": tx_hash,
        "value_sent": "0.00000000",
        "value_received": "1.50000000",
        "balance_change": "1.50000000",
        "time": time,
        "block": 5000000,
        "price": {"value": "0.10000000", "currency": "USD"},
    }


def test_balance_without_key_sends_no_key_header() -> None:
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE}/balance/DOGE/{_ADDRESS}", text=_success({"confirmed": "12.30000001", "unconfirmed": "-0.10000000"}))
        output = _read("address_balances", _CONFIG)

        assert [record.record.data for record in output.records] == [
            {"confirmed": "12.30000001", "unconfirmed": "-0.10000000", "network": "DOGE", "address": _ADDRESS}
        ]
        assert "API-KEY" not in mocker.last_request.headers


def test_empty_key_sends_no_key_header() -> None:
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE}/balance/DOGE/{_ADDRESS}", text=_success({"confirmed": "0.00000000", "unconfirmed": "0.00000000"}))
        _read("address_balances", {**_CONFIG, "api_key": ""})

        assert "API-KEY" not in mocker.last_request.headers


def test_key_is_sent_as_api_key_header() -> None:
    with HttpMocker() as http_mocker:
        request = HttpRequest(f"{_BASE}/address_summary/DOGE/{_ADDRESS}", headers={"API-KEY": "test-key"})
        summary = {
            "txs_sent": 3,
            "txs_received": 5,
            "txs_total": 7,
            "confirmed_balance": "12.30000001",
            "unconfirmed_balance": "0.00000000",
            "confirmed_received": "100.00000003",
            "first_active": {"height": 1, "time": 1386325540},
            "last_active": {"height": 2, "time": 1386325600},
        }
        http_mocker.get(request, HttpResponse(_success(summary)))
        output = _read("address_summaries", {**_CONFIG, "api_key": "test-key"})

        assert output.records[0].record.data["txs_total"] == 7
        assert output.records[0].record.data["confirmed_received"] == "100.00000003"
        http_mocker.assert_number_of_calls(request, 1)


def test_one_partition_per_address() -> None:
    other = "D8vFz4p1L37jdg9xpTx8s5hpXDnvxPpFRE"
    with requests_mock.Mocker() as mocker:
        for address in (_ADDRESS, other):
            mocker.get(f"{_BASE}/balance/DOGE/{address}", text=_success({"confirmed": "1.00000000", "unconfirmed": "0.00000000"}))
        output = _read("address_balances", {**_CONFIG, "addresses": [_ADDRESS, other]})

        assert sorted(record.record.data["address"] for record in output.records) == sorted([_ADDRESS, other])


@freeze_time("2026-01-02T00:00:00Z")
def test_transactions_follow_next_cursor() -> None:
    first = HttpRequest(
        f"{_BASE}/transactions/DOGE/{_ADDRESS}",
        query_params={"unconfirmed": "exclude", "page_size": "100", "from_time": "1767225600"},
    )
    second = HttpRequest(
        f"{_BASE}/transactions/DOGE/{_ADDRESS}",
        query_params={"unconfirmed": "exclude", "page_size": "100", "from_time": "1767225600", "cursor": "next-1"},
    )
    with HttpMocker() as http_mocker:
        http_mocker.get(
            first, HttpResponse(_success({"transactions": [_tx("a" * 64, 1767300000)], "next_cursor": "next-1", "page_size": 100}))
        )
        http_mocker.get(
            second, HttpResponse(_success({"transactions": [_tx("b" * 64, 1767250000)], "next_cursor": None, "page_size": 100}))
        )
        output = _read("address_transactions", {**_CONFIG, "start_date": "2026-01-01"}, SyncMode.incremental)

        assert [record.record.data["hash"] for record in output.records] == ["a" * 64, "b" * 64]
        assert output.records[0].record.data["network"] == "DOGE"
        assert output.records[0].record.data["address"] == _ADDRESS
        assert output.records[0].record.data["value_received"] == "1.50000000"
        http_mocker.assert_number_of_calls(first, 1)
        http_mocker.assert_number_of_calls(second, 1)


@freeze_time("2026-01-02T00:00:00Z")
def test_transactions_without_start_date_sync_full_history() -> None:
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE}/transactions/DOGE/{_ADDRESS}", text=_success({"transactions": [], "next_cursor": None, "page_size": 100}))
        _read("address_transactions", _CONFIG, SyncMode.incremental)

        assert mocker.last_request.qs["from_time"] == ["1230940800"]


@freeze_time("2026-01-02T00:00:00Z")
def test_transactions_resume_from_state_with_lookback() -> None:
    state = (
        StateBuilder()
        .with_stream_state(
            "address_transactions",
            {"states": [{"partition": {"address": _ADDRESS}, "cursor": {"time": "1767250000"}}]},
        )
        .build()
    )
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE}/transactions/DOGE/{_ADDRESS}", text=_success({"transactions": [], "next_cursor": None, "page_size": 100}))
        _read("address_transactions", _CONFIG, SyncMode.incremental, state=state)

        assert mocker.last_request.qs["from_time"] == [str(1767250000 - 3 * 3600)]


def test_bad_key_is_a_config_error() -> None:
    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"{_BASE}/balance/DOGE/{_ADDRESS}",
            status_code=401,
            text=json.dumps({"status": "fail", "data": {"error_message": "Invalid API key."}}),
        )
        output = _read("address_balances", {**_CONFIG, "api_key": "wrong"}, expecting_exception=True)

        assert any("SoChain rejected the API key" in (error.trace.error.message or "") for error in output.errors)


def test_unknown_address_reports_the_api_message() -> None:
    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"{_BASE}/balance/DOGE/{_ADDRESS}",
            status_code=404,
            text=json.dumps({"status": "fail", "data": {"error_message": "Unable to fetch address balance. Invalid address?"}}),
        )
        output = _read("address_balances", _CONFIG, expecting_exception=True)

        assert any("Invalid address?" in (error.trace.error.message or "") for error in output.errors)


def test_network_info() -> None:
    with requests_mock.Mocker() as mocker:
        info = {
            "block_count": 5000000,
            "best_block_hash": "c" * 64,
            "hashrate": "1000",
            "mempool": {"mempool_txs": 1, "mempool_size": 250, "updated_at": 1767225600, "blocks": []},
        }
        mocker.get(f"{_BASE}/network_info/DOGE", text=_success(info))
        output = _read("network_info", _CONFIG)

        assert output.records[0].record.data == {**info, "network": "DOGE"}


@pytest.fixture(scope="module")
def manifest() -> Mapping[str, Any]:
    with _MANIFEST_PATH.open() as manifest_file:
        return yaml.safe_load(manifest_file)


def test_api_key_is_optional_and_secret(manifest: Mapping[str, Any]) -> None:
    spec = manifest["spec"]["connection_specification"]

    assert "api_key" not in spec["required"]
    assert spec["properties"]["api_key"]["airbyte_secret"] is True
    assert "BTCTEST" in spec["properties"]["network"]["enum"]
