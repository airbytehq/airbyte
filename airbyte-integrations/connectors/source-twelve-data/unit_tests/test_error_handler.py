# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path
from typing import Any, Dict, Iterator
from unittest import TestCase
from unittest.mock import patch

import yaml
from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_SOURCE_FOLDER = Path(__file__).parent.parent
_COMPOSITE_ERROR_HANDLER = "".join(("Composite", "ErrorHandler"))
_STREAMS_WITH_ERROR_HANDLERS = (
    "stocks",
    "forex_pairs",
    "crypto_currencies",
    "funds",
    "bonds",
    "etfs",
    "commodities",
    "exchanges",
    "time_series",
    "exchange_rate",
    "quote",
    "price",
    "eod_price",
    "mutual_funds",
)
_URL_BASE = "https://api.twelvedata.com"
_CONFIG = {"api_key": "test_key", "country": "US", "exchange": "NASDAQ", "symbol": "AAPL", "interval": "1day"}

_STOCKS_REQUEST = HttpRequest(
    f"{_URL_BASE}/stocks",
    query_params={"apikey": "test_key", "country": "US", "exchange": "NASDAQ", "symbol": "AAPL"},
)
_AAPL_TIME_SERIES_REQUEST = HttpRequest(
    f"{_URL_BASE}/time_series",
    query_params={"apikey": "test_key", "symbol": "AAPL", "interval": "1day"},
)
_MSFT_TIME_SERIES_REQUEST = HttpRequest(
    f"{_URL_BASE}/time_series",
    query_params={"apikey": "test_key", "symbol": "MSFT", "interval": "1day"},
)


def _walk_nodes(value: Any) -> Iterator[Dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk_nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_nodes(child)


def _read(stream_name: str, expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(config=_CONFIG), _CONFIG, catalog, expecting_exception=expecting_exception)


def _mock_parent_stocks(http_mocker: HttpMocker) -> None:
    http_mocker.get(
        _STOCKS_REQUEST,
        HttpResponse(body=json.dumps({"data": [{"symbol": "AAPL"}, {"symbol": "MSFT"}]}), status_code=200),
    )


def _read_time_series_with_error(http_mocker: HttpMocker, status_code: int) -> EntrypointOutput:
    _mock_parent_stocks(http_mocker)
    http_mocker.get(
        _AAPL_TIME_SERIES_REQUEST,
        HttpResponse(body=json.dumps({"message": "Symbol is not available"}), status_code=status_code),
    )
    http_mocker.get(
        _MSFT_TIME_SERIES_REQUEST,
        HttpResponse(body=json.dumps({"values": [{"datetime": "2026-10-30"}]}), status_code=200),
    )
    return _read("time_series")


def test_no_composite_error_handlers() -> None:
    manifest = yaml.safe_load((_SOURCE_FOLDER / "manifest.yaml").read_text())

    assert all(node.get("type") != _COMPOSITE_ERROR_HANDLER for node in _walk_nodes(manifest))
    for stream_name in _STREAMS_WITH_ERROR_HANDLERS:
        error_handler = manifest["definitions"]["streams"][stream_name]["retriever"]["requester"]["error_handler"]
        assert error_handler["type"] == "DefaultErrorHandler"


@patch("time.sleep", lambda _: None)
class TestTwelveDataErrorHandler(TestCase):
    @HttpMocker()
    def test_429_is_retried_then_succeeds(self, http_mocker: HttpMocker) -> None:
        rate_limit_message = "Wait for the next minute or consider switching to a higher tier plan at " "https://twelvedata.com/pricing"
        http_mocker.get(
            _STOCKS_REQUEST,
            [
                HttpResponse(body=rate_limit_message, status_code=429),
                HttpResponse(body=json.dumps({"data": [{"symbol": "AAPL"}]}), status_code=200),
            ],
        )

        output = _read("stocks")

        assert len(output.records) == 1
        assert output.errors == []
        http_mocker.assert_number_of_calls(_STOCKS_REQUEST, 2)

    @HttpMocker()
    def test_stocks_403_fails_without_retry(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_STOCKS_REQUEST, HttpResponse(body="Forbidden", status_code=403))

        output = _read("stocks", expecting_exception=True)

        assert output.errors
        http_mocker.assert_number_of_calls(_STOCKS_REQUEST, 1)

    @HttpMocker()
    def test_time_series_404_is_ignored_for_one_symbol(self, http_mocker: HttpMocker) -> None:
        output = _read_time_series_with_error(http_mocker, 404)

        assert [record.record.data["symbol"] for record in output.records] == ["MSFT"]
        assert output.errors == []
        http_mocker.assert_number_of_calls(_STOCKS_REQUEST, 1)
        http_mocker.assert_number_of_calls(_AAPL_TIME_SERIES_REQUEST, 1)
        http_mocker.assert_number_of_calls(_MSFT_TIME_SERIES_REQUEST, 1)

    @HttpMocker()
    def test_time_series_403_is_ignored_for_one_symbol(self, http_mocker: HttpMocker) -> None:
        output = _read_time_series_with_error(http_mocker, 403)

        assert [record.record.data["symbol"] for record in output.records] == ["MSFT"]
        assert output.errors == []
        http_mocker.assert_number_of_calls(_STOCKS_REQUEST, 1)
        http_mocker.assert_number_of_calls(_AAPL_TIME_SERIES_REQUEST, 1)
        http_mocker.assert_number_of_calls(_MSFT_TIME_SERIES_REQUEST, 1)

    @HttpMocker()
    def test_500_is_retried_then_succeeds(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _STOCKS_REQUEST,
            [
                HttpResponse(body="", status_code=500),
                HttpResponse(body=json.dumps({"data": [{"symbol": "AAPL"}]}), status_code=200),
            ],
        )

        output = _read("stocks")

        assert len(output.records) == 1
        assert output.errors == []
        http_mocker.assert_number_of_calls(_STOCKS_REQUEST, 2)
