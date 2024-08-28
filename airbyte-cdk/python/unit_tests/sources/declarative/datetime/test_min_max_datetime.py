#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime

import pytest
from airbyte_cdk.sources.declarative.datetime.min_max_datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString

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
        ("test_min_newer_time_from_parameters", "{{ config['older'] }}", "{{ parameters['newer'] }}", "", new_date),
        ("test_max_newer_time_from_parameters", "{{ stream_state['newer'] }}", "", "{{ parameters['older'] }}", old_date),
    ],
)
def test_min_max_datetime(test_name, date, min_date, max_date, expected_date):
    config = {"older": old_date, "middle": middle_date}
    stream_state = {"newer": new_date}
    parameters = {"newer": new_date, "older": old_date}

    min_max_date = MinMaxDatetime(datetime=date, min_datetime=min_date, max_datetime=max_date, parameters=parameters)
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
        parameters={},
    )
    actual_date = min_max_date.get_datetime(config, **{"stream_state": stream_state})

    assert actual_date == datetime.datetime.strptime("2022-01-01T20:12:19", "%Y-%m-%dT%H:%M:%S").replace(tzinfo=datetime.timezone.utc)


def test_format_is_a_number():
    config = {"older": "20210101", "middle": "20220101"}
    stream_state = {"newer": "20220624"}

    min_max_date = MinMaxDatetime(
        datetime="{{ config['middle'] }}",
        datetime_format="%Y%m%d",
        min_datetime="{{ config['older'] }}",
        max_datetime="{{ stream_state['newer'] }}",
        parameters={},
    )
    actual_date = min_max_date.get_datetime(config, **{"stream_state": stream_state})

    assert actual_date == datetime.datetime.strptime("20220101", "%Y%m%d").replace(tzinfo=datetime.timezone.utc)


def test_set_datetime_format():
    min_max_date = MinMaxDatetime(datetime="{{ config['middle'] }}", min_datetime="{{ config['older'] }}", parameters={})

    # Retrieve datetime using the default datetime formatting
    default_fmt_config = {"older": "2021-01-01T20:12:19.597854Z", "middle": "2022-01-01T20:12:19.597854Z"}
    actual_date = min_max_date.get_datetime(default_fmt_config)

    assert actual_date == datetime.datetime.strptime("2022-01-01T20:12:19.597854Z", "%Y-%m-%dT%H:%M:%S.%f%z")

    # Set a different datetime format and attempt to retrieve datetime using an updated format
    min_max_date.datetime_format = "%Y-%m-%dT%H:%M:%S"

    custom_fmt_config = {"older": "2021-01-01T20:12:19", "middle": "2022-01-01T20:12:19"}
    actual_date = min_max_date.get_datetime(custom_fmt_config)

    assert actual_date == datetime.datetime.strptime("2022-01-01T20:12:19", "%Y-%m-%dT%H:%M:%S").replace(tzinfo=datetime.timezone.utc)


def test_min_max_datetime_lazy_eval():
    kwargs = {
        "datetime": "2022-01-10T00:00:00",
        "datetime_format": "%Y-%m-%dT%H:%M:%S",
        "min_datetime": "{{ parameters.min_datetime }}",
        "max_datetime": "{{ parameters.max_datetime }}",
    }

    assert datetime.datetime(2022, 1, 10, 0, 0, tzinfo=datetime.timezone.utc) == MinMaxDatetime(**kwargs, parameters={}).get_datetime({})
    assert datetime.datetime(2022, 1, 20, 0, 0, tzinfo=datetime.timezone.utc) == MinMaxDatetime(
        **kwargs, parameters={"min_datetime": "2022-01-20T00:00:00"}
    ).get_datetime({})
    assert datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc) == MinMaxDatetime(
        **kwargs, parameters={"max_datetime": "2021-01-01T00:00:00"}
    ).get_datetime({})


@pytest.mark.parametrize(
    "input_datetime", [
        pytest.param("2022-01-01T00:00:00", id="test_create_min_max_datetime_from_string"),
        pytest.param(InterpolatedString.create("2022-01-01T00:00:00", parameters={}), id="test_create_min_max_datetime_from_string"),
        pytest.param(MinMaxDatetime("2022-01-01T00:00:00", parameters={}), id="test_create_min_max_datetime_from_minmaxdatetime")
    ]
)
def test_create_min_max_datetime(input_datetime):
    minMaxDatetime = MinMaxDatetime.create(input_datetime, parameters={})
    expected_value = "2022-01-01T00:00:00"

    assert minMaxDatetime.datetime.eval(config={}) == expected_value
