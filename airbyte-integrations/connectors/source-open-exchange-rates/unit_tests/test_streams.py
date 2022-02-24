#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock
from datetime import date

import pytest

from airbyte_cdk.models import SyncMode
from source_open_exchange_rates.streams import HistoricalExchangeRates



def test_request_params():
    stream = HistoricalExchangeRates(app_id=pytest.oxr_app_id, start_date=pytest.oxr_start_date)
    inputs = {"stream_slice": [{"date": "2022-02-01"}, {"date": "2022-02-02"}], "stream_state": None, "next_page_token": None}

    expected_params = {'app_id': 'my_unit_test_app_id', 'start_date': '2022-02-01', 'show_alternative': False, 'prettyprint': False}
    assert stream.request_params(**inputs) == expected_params


def test_parse_response():
    stream = HistoricalExchangeRates(app_id=pytest.oxr_app_id, start_date=pytest.oxr_start_date)

    response_mock = MagicMock()
    response_mock.json.return_value = {"disclaimer":"Usage subject to terms: https://openexchangerates.org/terms","license":"https://openexchangerates.org/license","timestamp":1644364799,"base":"EUR","rates":{"AED":4.194864,"AFN":108.57929,"ALL":121.321065}}
    inputs = {"response": response_mock}

    expected_parsed_object = {"timestamp":1644364799,"base":"EUR","rates":{"AED":4.194864,"AFN":108.57929,"ALL":121.321065}}
    assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_request_headers():
    stream = HistoricalExchangeRates(app_id=pytest.oxr_app_id, start_date=pytest.oxr_start_date)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method():
    stream = HistoricalExchangeRates(app_id=pytest.oxr_app_id, start_date=pytest.oxr_start_date)
    expected_method = "GET"
    assert stream.http_method == expected_method


@pytest.mark.parametrize(
    ("http_status", "should_retry"),
    [
        (HTTPStatus.OK, False),
        (HTTPStatus.BAD_REQUEST, False),
        (HTTPStatus.TOO_MANY_REQUESTS, True),
        (HTTPStatus.INTERNAL_SERVER_ERROR, True),
    ],
)
def test_should_retry(http_status, should_retry):
    response_mock = MagicMock()
    response_mock.status_code = http_status
    stream = HistoricalExchangeRates(app_id=pytest.oxr_app_id, start_date=pytest.oxr_start_date)
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time():
    response_mock = MagicMock()
    stream = HistoricalExchangeRates(app_id=pytest.oxr_app_id, start_date=pytest.oxr_start_date)
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time


def test_cursor_field():
    stream = HistoricalExchangeRates(app_id=pytest.oxr_app_id, start_date=pytest.oxr_start_date)
    expected_cursor_field = ["timestamp"]
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state():
    stream = HistoricalExchangeRates(app_id=pytest.oxr_app_id, start_date=pytest.oxr_start_date)
    inputs = {"current_stream_state": {"timestamp": 1644190000}, "latest_record": {"timestamp": 1644191999, "base": "EUR", "rates":{"AED":4.194864,"AFN":108.57929,"ALL":121.321065}}}
    expected_state = {"timestamp": 1644191999}
    assert stream.get_updated_state(**inputs) == expected_state


def test_stream_slices():
    start_date = date.today()
    start_date = start_date.replace(day=start_date.day - 2)
    stream = HistoricalExchangeRates(app_id=pytest.oxr_app_id, start_date=str(start_date))

    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": ["timestamp"], "stream_state": {"timestamp": 1644191999}}
    expected_stream_slice = [{"date": str(start_date)}, {"date":  str(start_date.replace(day=start_date.day + 1))}]
    assert stream.stream_slices(**inputs) == expected_stream_slice


def test_supports_incremental(mocker):
    mocker.patch.object(HistoricalExchangeRates, "cursor_field", "dummy_field")
    stream = HistoricalExchangeRates(app_id=pytest.oxr_app_id, start_date=pytest.oxr_start_date)
    assert stream.supports_incremental


def test_source_defined_cursor():
    stream = HistoricalExchangeRates(app_id=pytest.oxr_app_id, start_date=pytest.oxr_start_date)
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval():
    stream = HistoricalExchangeRates(app_id=pytest.oxr_app_id, start_date=pytest.oxr_start_date)
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
