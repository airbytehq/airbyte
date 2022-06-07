#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString

config = {"field": "value"}


def test_static_value():
    static_value = "HELLO WORLD"
    s = InterpolatedString(static_value)
    assert s.eval(config) == "HELLO WORLD"


def test_eval_from_config():
    string = "{{ config['field'] }}"
    s = InterpolatedString(string)
    assert s.eval(config) == "value"


def test_eval_from_kwargs():
    string = "{{ kwargs['c'] }}"
    kwargs = {"c": "airbyte"}
    s = InterpolatedString(string)
    assert s.eval(config, **{"kwargs": kwargs}) == "airbyte"
