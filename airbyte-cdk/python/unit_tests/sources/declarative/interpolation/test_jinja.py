#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime

import pytest
from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation

interpolation = JinjaInterpolation()


def test_get_value_from_config():
    s = "{{ config['date'] }}"
    config = {"date": "2022-01-01"}
    val = interpolation.eval(s, config)
    assert val == "2022-01-01"


def test_get_value_from_stream_slice():
    s = "{{ stream_slice['date'] }}"
    config = {"date": "2022-01-01"}
    stream_slice = {"date": "2020-09-09"}
    val = interpolation.eval(s, config, **{"stream_slice": stream_slice})
    assert val == "2020-09-09"


def test_get_value_from_a_list_of_mappings():
    s = "{{ records[0]['date'] }}"
    config = {"date": "2022-01-01"}
    records = [{"date": "2020-09-09"}]
    val = interpolation.eval(s, config, **{"records": records})
    assert val == "2020-09-09"


@pytest.mark.parametrize(
    "test_name, s, value",
    [
        ("test_number", "{{1}}", 1),
        ("test_list", "{{[1,2]}}", [1, 2]),
        ("test_dict", "{{ {1:2} }}", {1: 2}),
        ("test_addition", "{{ 1+2 }}", 3),
    ],
)
def test_literals(test_name, s, value):
    val = interpolation.eval(s, None)
    assert val == value


def test_positive_day_delta():
    delta_template = "{{ day_delta(25) }}"
    interpolation = JinjaInterpolation()
    val = interpolation.eval(delta_template, {})

    # We need to assert against an earlier delta since the interpolation function runs datetime.now() a few milliseconds earlier
    assert val > (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=24, hours=23)).strftime("%Y-%m-%dT%H:%M:%S.%f%z")


def test_negative_day_delta():
    delta_template = "{{ day_delta(-25) }}"
    interpolation = JinjaInterpolation()
    val = interpolation.eval(delta_template, {})

    assert val <= (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=25)).strftime("%Y-%m-%dT%H:%M:%S.%f%z")


@pytest.mark.parametrize(
    "test_name, s, expected_value",
    [
        ("test_timestamp_from_timestamp", "{{ timestamp(1621439283) }}", 1621439283),
        ("test_timestamp_from_string", "{{ timestamp('2021-05-19') }}", 1621382400),
        ("test_timestamp_from_rfc3339", "{{ timestamp('2017-01-01T00:00:00.0Z') }}", 1483228800),
        ("test_max", "{{ max(1,2) }}", 2),
    ],
)
def test_macros(test_name, s, expected_value):
    interpolation = JinjaInterpolation()
    config = {}
    val = interpolation.eval(s, config)
    assert val == expected_value
