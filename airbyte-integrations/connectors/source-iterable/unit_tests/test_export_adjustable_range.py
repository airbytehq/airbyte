#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime
import json
import urllib.parse
from typing import List
from unittest import mock

import freezegun
import pendulum
import pytest
import responses
from requests.exceptions import ChunkedEncodingError
from source_iterable.slice_generators import AdjustableSliceGenerator
from source_iterable.source import SourceIterable

TEST_START_DATE = "2020"


@pytest.fixture
def time_mock(request):
    with freezegun.freeze_time() as time_mock:
        yield time_mock


def get_range_days_from_request(request):
    query = urllib.parse.urlsplit(request.url).query
    query = urllib.parse.parse_qs(query)
    return (pendulum.parse(query["endDateTime"][0]) - pendulum.parse(query["startDateTime"][0])).days


@mock.patch("logging.getLogger", mock.MagicMock())
def read_from_source(catalog):
    return list(
        SourceIterable().read(
            mock.MagicMock(),
            {"start_date": TEST_START_DATE, "api_key": "api_key"},
            catalog,
            None,
        )
    )


@responses.activate
@pytest.mark.parametrize("catalog", (["email_send"]), indirect=True)
def test_email_stream(catalog, time_mock):
    DAYS_DURATION = 100
    DAYS_PER_MINUTE_RATE = 8

    time_mock.move_to(pendulum.parse(TEST_START_DATE) + pendulum.Duration(days=DAYS_DURATION))

    ranges: List[int] = []

    def response_cb(req):
        days = get_range_days_from_request(req)
        ranges.append(days)
        time_mock.tick(delta=datetime.timedelta(minutes=days / DAYS_PER_MINUTE_RATE))
        return (200, {}, json.dumps({"createdAt": "2020"}))

    responses.add_callback("GET", "https://api.iterable.com/api/export/data.json", callback=response_cb)

    records = read_from_source(catalog)
    assert records
    assert sum(ranges) == DAYS_DURATION
    assert len(responses.calls) == len(ranges)
    assert ranges == [
        AdjustableSliceGenerator.INITIAL_RANGE_DAYS,
        *([int(DAYS_PER_MINUTE_RATE / AdjustableSliceGenerator.REQUEST_PER_MINUTE_LIMIT)] * 35),
    ]


@responses.activate
@pytest.mark.parametrize(
    "catalog, days_duration, days_per_minute_rate",
    [
        ("email_send", 10, 200),
        # ("email_send", 100, 200000),
        # ("email_send", 10000, 200000),
        # ("email_click", 1000, 20),
        # ("email_open", 1000, 1),
        ("email_open", 1, 1000),
        ("email_open", 0, 1000000),
    ],
    indirect=["catalog"],
)
def test_email_stream_chunked_encoding(catalog, days_duration, days_per_minute_rate, time_mock):
    time_mock.move_to(pendulum.parse(TEST_START_DATE) + pendulum.Duration(days=days_duration))

    ranges: List[int] = []
    encoding_throw = 0

    def response_cb(req):
        nonlocal encoding_throw
        # Every request fails with 2 ChunkedEncodingError exception but works well on third time.
        if encoding_throw < 2:
            encoding_throw += 1
            raise ChunkedEncodingError()
        encoding_throw = 0
        days = get_range_days_from_request(req)
        ranges.append(days)
        time_mock.tick(delta=datetime.timedelta(minutes=days / days_per_minute_rate))
        return (200, {}, json.dumps({"createdAt": "2020"}))

    responses.add_callback("GET", "https://api.iterable.com/api/export/data.json", callback=response_cb)

    records = read_from_source(catalog)
    assert sum(ranges) == days_duration
    assert len(ranges) == len(records)
    assert len(responses.calls) == 3 * len(ranges)


@responses.activate
@pytest.mark.parametrize("catalog", (["email_send"]), indirect=True)
def test_email_stream_chunked_encoding_exception(catalog, time_mock):
    TEST_START_DATE = "2020"
    DAYS_DURATION = 100

    time_mock.move_to(pendulum.parse(TEST_START_DATE) + pendulum.Duration(days=DAYS_DURATION))

    responses.add(
        "GET",
        "https://api.iterable.com/api/export/data.json",
        body=ChunkedEncodingError(),
    )

    with pytest.raises(Exception, match="ChunkedEncodingError: Reached maximum number of retires: 3"):
        read_from_source(catalog)
    assert len(responses.calls) == 15
