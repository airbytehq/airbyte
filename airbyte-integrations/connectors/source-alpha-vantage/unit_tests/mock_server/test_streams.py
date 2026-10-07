# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import gzip
import json
import logging
from pathlib import Path

import pytest
from conftest import get_source

from airbyte_cdk.models import Status, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import discover, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_CONFIG = {
    "api_key": "test_key",
    "symbol": "IBM",
    "interval": "5min",
    "adjusted": False,
    "outputsize": "compact",
}

_RESPONSE_DIR = Path(__file__).parent.parent / "resource" / "http" / "response"

# (stream_name, api function, JSON series key, key field injected by the old extractor)
_TIME_SERIES_STREAMS = [
    ("time_series_intraday", "TIME_SERIES_INTRADAY", "Time Series (5min)", "timestamp"),
    ("time_series_daily", "TIME_SERIES_DAILY", "Time Series (Daily)", "date"),
    ("time_series_daily_adjusted", "TIME_SERIES_DAILY_ADJUSTED", "Time Series (Daily)", "date"),
    ("time_series_weekly", "TIME_SERIES_WEEKLY", "Weekly Time Series", "date"),
    ("time_series_weekly_adjusted", "TIME_SERIES_WEEKLY_ADJUSTED", "Weekly Adjusted Time Series", "date"),
    ("time_series_monthly", "TIME_SERIES_MONTHLY", "Monthly Time Series", "date"),
    ("time_series_monthly_adjusted", "TIME_SERIES_MONTHLY_ADJUSTED", "Monthly Adjusted Time Series", "date"),
]

_STREAM_NAMES = [s[0] for s in _TIME_SERIES_STREAMS] + ["quote"]


def _fixture(name: str) -> str:
    return (_RESPONSE_DIR / name).read_text()


def _request(function: str, datatype: str) -> HttpRequest:
    return HttpRequest(
        url="https://www.alphavantage.co/query",
        query_params={
            "apikey": _CONFIG["api_key"],
            "symbol": _CONFIG["symbol"],
            "function": function,
            "datatype": datatype,
            "outputsize": _CONFIG["outputsize"],
            "interval": _CONFIG["interval"],
            "adjusted": "False",
        },
    )


def _read_stream(stream_name: str, config: dict):
    source = get_source(config)
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(source, config, catalog)


@pytest.mark.parametrize(
    "stream_name,function,series_key,key_field",
    _TIME_SERIES_STREAMS,
    ids=[s[0] for s in _TIME_SERIES_STREAMS],
)
def test_time_series_records_match_legacy_extractor(stream_name, function, series_key, key_field):
    """Emitted records must be identical to what the old ObjectDpathExtractor produced."""
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request(function, "csv"),
            HttpResponse(gzip.compress(_fixture(f"{stream_name}.csv").encode()), headers={"Content-Encoding": "gzip"}),
        )

        output = _read_stream(stream_name, _CONFIG)

    body = json.loads(_fixture(f"{stream_name}.json"))
    expected = [{key_field: key, **value} for key, value in body[series_key].items()]
    actual = [record.record.data for record in output.records]
    assert actual == expected
    assert len(actual) == 3
    assert isinstance(actual[0]["1. open"], str)


@pytest.mark.parametrize(
    "stream_name,function",
    [(s[0], s[1]) for s in _TIME_SERIES_STREAMS],
    ids=[s[0] for s in _TIME_SERIES_STREAMS],
)
def test_time_series_information_message_yields_no_records(stream_name, function):
    """Alpha Vantage returns a JSON throttle/error body even for datatype=csv; it must be filtered out."""
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request(function, "csv"),
            HttpResponse(gzip.compress(_fixture("information_message.json").encode()), headers={"Content-Encoding": "gzip"}),
        )

        output = _read_stream(stream_name, _CONFIG)

    assert output.records == []
    assert output.errors == []


def test_quote_returns_single_record():
    with HttpMocker() as http_mocker:
        http_mocker.get(_request("GLOBAL_QUOTE", "json"), HttpResponse(_fixture("global_quote.json")))

        output = _read_stream("quote", _CONFIG)

    actual = [record.record.data for record in output.records]
    assert actual == [json.loads(_fixture("global_quote.json"))]


def test_quote_information_message_yields_no_records():
    with HttpMocker() as http_mocker:
        http_mocker.get(_request("GLOBAL_QUOTE", "json"), HttpResponse(_fixture("information_message.json")))

        output = _read_stream("quote", _CONFIG)

    assert output.records == []
    assert output.errors == []


def test_discover_all_streams():
    output = discover(get_source(_CONFIG), _CONFIG)

    streams = {stream.name: stream for stream in output.catalog.catalog.streams}
    assert set(streams.keys()) == set(_STREAM_NAMES)
    assert "05. price" in streams["quote"].json_schema["properties"]["Global Quote"]["properties"]


def test_check_succeeds():
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("TIME_SERIES_WEEKLY", "csv"),
            HttpResponse(gzip.compress(_fixture("time_series_weekly.csv").encode()), headers={"Content-Encoding": "gzip"}),
        )
        http_mocker.get(
            _request("TIME_SERIES_WEEKLY_ADJUSTED", "csv"),
            HttpResponse(gzip.compress(_fixture("time_series_weekly_adjusted.csv").encode()), headers={"Content-Encoding": "gzip"}),
        )

        status = get_source(_CONFIG).check(logging.getLogger("airbyte"), _CONFIG)

    assert status.status == Status.SUCCEEDED
