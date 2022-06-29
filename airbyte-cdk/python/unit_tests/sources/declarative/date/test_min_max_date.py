#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime

import pytest
from airbyte_cdk.sources.declarative.date.min_max_date import MinMaxDate

date_format = "%Y-%m-%dT%H:%M:%S.%f%z"


@pytest.mark.parametrize(
    "test_name, date, min_date, max_date, expected_date",
    [
        ("test_time_is_greater_than_min", "{{ config['older'] }}", "{{ stream_state['newer'] }}", "", "2022-06-24T20:12:19.597854Z"),
        ("test_time_is_less_than_min", "{{ stream_state['newer'] }}", "{{ config['older'] }}", "", "2022-06-24T20:12:19.597854Z"),
        ("test_time_is_equal_to_min", "{{ config['older'] }}", "{{ config['older'] }}", "", "2021-01-01T20:12:19.597854Z"),
        ("test_time_is_greater_than_max", "{{ stream_state['newer'] }}", "", "{{ config['older'] }}", "2021-01-01T20:12:19.597854Z"),
        ("test_time_is_less_than_max", "{{ config['older'] }}", "", "{{ stream_state['newer'] }}", "2021-01-01T20:12:19.597854Z"),
        ("test_time_is_equal_to_min", "{{ stream_state['newer'] }}", "{{ stream_state['newer'] }}", "", "2022-06-24T20:12:19.597854Z"),
        (
            "test_time_is_between_min_and_max",
            "{{ config['middle'] }}",
            "{{ config['older'] }}",
            "{{ stream_state['newer'] }}",
            "2022-01-01T20:12:19.597854Z",
        ),
    ],
)
def test_min_max_time(test_name, date, min_date, max_date, expected_date):
    config = {"older": "2021-01-01T20:12:19.597854Z", "middle": "2022-01-01T20:12:19.597854Z"}
    stream_state = {"newer": "2022-06-24T20:12:19.597854Z"}

    min_max_date = MinMaxDate(date=date, min_date=min_date, max_date=max_date)
    actual_date = min_max_date.get_date(config, **{"stream_state": stream_state})

    assert actual_date == datetime.datetime.strptime(expected_date, date_format)


def test_custom_time_format():
    config = {"older": "2021-01-01T20:12:19", "middle": "2022-01-01T20:12:19"}
    stream_state = {"newer": "2022-06-24T20:12:19"}

    min_max_date = MinMaxDate(
        date="{{ config['middle'] }}",
        datetime_format="%Y-%m-%dT%H:%M:%S",
        min_date="{{ config['older'] }}",
        max_date="{{ stream_state['newer'] }}",
    )
    actual_date = min_max_date.get_date(config, **{"stream_state": stream_state})

    assert actual_date == datetime.datetime.strptime("2022-01-01T20:12:19", "%Y-%m-%dT%H:%M:%S").replace(tzinfo=datetime.timezone.utc)
