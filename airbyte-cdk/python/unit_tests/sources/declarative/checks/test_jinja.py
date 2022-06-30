#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation


def test_get_value_from_config():
    interpolation = JinjaInterpolation()
    s = "{{ config['date'] }}"
    config = {"date": "2022-01-01"}
    val = interpolation.eval(s, config)
    assert val == "2022-01-01"


def test_get_value_from_stream_slice():
    interpolation = JinjaInterpolation()
    s = "{{ stream_slice['date'] }}"
    config = {"date": "2022-01-01"}
    stream_slice = {"date": "2020-09-09"}
    val = interpolation.eval(s, config, **{"stream_slice": stream_slice})
    assert val == "2020-09-09"


def test_get_value_from_a_list_of_mappings():
    interpolation = JinjaInterpolation()
    s = "{{ records[0]['date'] }}"
    config = {"date": "2022-01-01"}
    records = [{"date": "2020-09-09"}]
    val = interpolation.eval(s, config, **{"records": records})
    assert val == "2020-09-09"


@pytest.mark.parametrize(
    "test_name, s, expected_value",
    [
        ("test_timestamp_from_timestamp", "{{ timestamp(1621439283) }}", 1621439283),
        ("test_timestamp_from_string", "{{ timestamp('2021-05-19') }}", 1621382400),
        ("test_timestamp_from_rfc3339", "{{ timestamp('2017-01-01T00:00:00.0Z') }}", 1483228800),
    ],
)
def test_timestamp(test_name, s, expected_value):
    interpolation = JinjaInterpolation()
    config = {}
    val = interpolation.eval(s, config)
    assert val == expected_value
