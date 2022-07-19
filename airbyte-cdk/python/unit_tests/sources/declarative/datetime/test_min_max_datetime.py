#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime

import pytest
from airbyte_cdk.sources.declarative.datetime.min_max_datetime import MinMaxDatetime

date_format = "%Y-%m-%dT%H:%M:%S.%f%z"

old_date = "2021-01-01T20:12:19.597854Z"
middle_date = "2022-01-01T20:12:19.597854Z"
new_date = "2022-06-24T20:12:19.597854Z"


@pytest.mark.parametrize(
    "test_name, date, min_date, max_date, expected_date",
    [
        ("test_time_is_greater_than_min", "{{ config['older'] }}", "{{ stream_state['newer'] }}", "", new_date),
        ("test_time_is_less_than_min", "{{ stream_state['newer'] }}", "{{ config['older'] }}", "", new_date),
        ("test_time_is_equal_to_min", "{{ config['older'] }}", "{{ config['older'] }}", "", old_date),
        ("test_time_is_greater_than_max", "{{ stream_state['newer'] }}", "", "{{ config['older'] }}", old_date),
        ("test_time_is_less_than_max", "{{ config['older'] }}", "", "{{ stream_state['newer'] }}", old_date),
        ("test_time_is_equal_to_min", "{{ stream_state['newer'] }}", "{{ stream_state['newer'] }}", "", new_date),
        (
            "test_time_is_between_min_and_max",
            "{{ config['middle'] }}",
            "{{ config['older'] }}",
            "{{ stream_state['newer'] }}",
            middle_date,
        ),
    ],
)
def test_min_max_datetime(test_name, date, min_date, max_date, expected_date):
    config = {"older": old_date, "middle": middle_date}
    stream_state = {"newer": new_date}

    min_max_date = MinMaxDatetime(datetime=date, min_datetime=min_date, max_datetime=max_date)
    actual_date = min_max_date.get_datetime(config, **{"stream_state": stream_state})

    assert actual_date == datetime.datetime.strptime(expected_date, date_format)


def test_custom_datetime_format():
    config = {"older": "2021-01-01T20:12:19", "middle": "2022-01-01T20:12:19"}
    stream_state = {"newer": "2022-06-24T20:12:19"}

    min_max_date = MinMaxDatetime(
        datetime="{{ config['middle'] }}",
        datetime_format="%Y-%m-%dT%H:%M:%S",
        min_datetime="{{ config['older'] }}",
        max_datetime="{{ stream_state['newer'] }}",
    )
    actual_date = min_max_date.get_datetime(config, **{"stream_state": stream_state})

    assert actual_date == datetime.datetime.strptime("2022-01-01T20:12:19", "%Y-%m-%dT%H:%M:%S").replace(tzinfo=datetime.timezone.utc)
