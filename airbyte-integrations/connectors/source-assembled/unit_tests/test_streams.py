#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pendulum
import pytest
from freezegun import freeze_time
from source_assembled.source import PAGE_LIMIT, AssembledStream, chunk_date_range


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(AssembledStream, "path", "v0/example_endpoint")
    mocker.patch.object(AssembledStream, "primary_key", "test_primary_key")
    mocker.patch.object(AssembledStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = AssembledStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": 1000}
    expected_params = {
        "limit": PAGE_LIMIT,
        "offset": 1000,
    }
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class):
    stream = AssembledStream()

    response_mock = MagicMock()
    offset = 1000
    response_mock.json.return_value = {"total": 5000, "offset": offset}
    inputs = {"response": response_mock}

    expected_token = offset + PAGE_LIMIT
    assert stream.next_page_token(**inputs) == expected_token


def test_next_page_token_end(patch_base_class):
    stream = AssembledStream()

    response_mock = MagicMock()
    offset = 1000
    response_mock.json.return_value = {"total": 1000, "offset": offset}
    inputs = {"response": response_mock}

    expected_token = None
    assert stream.next_page_token(**inputs) == expected_token


def test_parse_response_result_is_dict(patch_base_class):
    stream = AssembledStream()

    response_mock = MagicMock()
    response_mock.json.return_value = {"data": {"id-one": {"id": "id-one"}, "id-two": {"id": "id-two"}}}
    inputs = {"response": response_mock}
    expected_parsed_object = {"id": "id-one"}
    assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_parse_response_result_not_dict(patch_base_class):
    stream = AssembledStream()
    stream.result_is_dict = False

    response_mock = MagicMock()
    response_mock.json.return_value = {"data": [{"id": "id-one"}]}
    inputs = {"response": response_mock}
    expected_parsed_object = {"id": "id-one"}
    assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_http_method(patch_base_class):
    stream = AssembledStream()
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
def test_should_retry(patch_base_class, http_status, should_retry):
    response_mock = MagicMock()
    response_mock.status_code = http_status
    stream = AssembledStream()
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = AssembledStream()
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time


@freeze_time("2022-01-30T18:23:33Z")
def test_chunk_date_range_without_end_date():
    start_timestamp = pendulum.parse("2022-01-24T18:23:00Z")
    start_date = start_timestamp.start_of("day")

    chunks = chunk_date_range(start_date=start_timestamp)
    first = next(chunks)

    assert pendulum.period(start_date, start_date.add(days=1)) == first

    *_, last = chunks

    last_period_end = pendulum.now("UTC").start_of("day")
    last_period_start = last_period_end.subtract(days=1)
    assert pendulum.period(last_period_start, last_period_end) == last

@freeze_time("2022-01-24T18:23:33Z")
def test_chunk_date_range_same_day():
    start_date = pendulum.parse("2022-01-24")

    chunks = list(chunk_date_range(start_date=start_date))
    assert len(chunks) == 0

def test_chunk_date_range():
    start_date = pendulum.parse("2022-01-24")
    end_date = pendulum.parse("2022-04-24")

    *_, last = chunk_date_range(start_date=start_date, end_date=end_date)
    assert pendulum.period(end_date.subtract(days=1), end_date) == last


def test_chunk_date_range_number_of_period_time_end():
    start_date = pendulum.parse("2022-01-24")
    end_date = pendulum.parse("2022-01-27T18:23:00Z")

    chunks = list(chunk_date_range(start_date=start_date, end_date=end_date))
    assert len(chunks) == 4


def test_chunk_date_range_number_of_period_day_end():
    start_date = pendulum.parse("2022-01-24")
    end_date = pendulum.parse("2022-01-27")

    chunks = list(chunk_date_range(start_date=start_date, end_date=end_date))
    assert len(chunks) == 3


def test_chunk_date_range_datetime_start_date():
    start_date = pendulum.parse("2022-01-24T18:23:00Z")
    end_date = pendulum.parse("2022-01-27")

    first = next(chunk_date_range(start_date=start_date, end_date=end_date))

    start_date = start_date.start_of("day")
    assert pendulum.period(start_date, start_date.add(days=1)) == first
