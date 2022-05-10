#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from airbyte_cdk.sources.cac.interpolation.eval import JinjaInterpolation


def test_get_value_from_config():
    interpolation = JinjaInterpolation()
    s = "{{ config['date'] }}"
    vars = {}
    config = {"date": "2022-01-01"}
    val = interpolation.eval(s, vars, config)
    assert val == "2022-01-01"


def test_get_value_from_vars():
    interpolation = JinjaInterpolation()
    s = "{{ vars['option'] }}"
    vars = {"option": "ABC"}
    config = {"date": "2022-01-01"}
    val = interpolation.eval(s, vars, config)
    assert val == "ABC"


def test_get_value_from_stream_slice():
    interpolation = JinjaInterpolation()
    s = "{{ stream_slice['date'] }}"
    vars = {"option": "ABC"}
    config = {"date": "2022-01-01"}
    stream_slice = {"date": "2020-09-09"}
    val = interpolation.eval(s, vars, config, **{"stream_slice": stream_slice})
    assert val == "2020-09-09"
