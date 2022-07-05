#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

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
