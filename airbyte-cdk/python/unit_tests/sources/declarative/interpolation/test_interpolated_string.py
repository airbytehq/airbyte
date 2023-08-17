#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString

config = {"field": "value"}
parameters = {"hello": "world"}
kwargs = {"c": "airbyte"}


@pytest.mark.parametrize(
    "test_name, input_string, expected_value",
    [
        ("test_static_value", "HELLO WORLD", "HELLO WORLD"),
        ("test_eval_from_parameters", "{{ parameters['hello'] }}", "world"),
        ("test_eval_from_config", "{{ config['field'] }}", "value"),
        ("test_eval_from_kwargs", "{{ kwargs['c'] }}", "airbyte"),
        ("test_eval_from_kwargs", "{{ kwargs['c'] }}", "airbyte"),
    ],
)
def test_interpolated_string(test_name, input_string, expected_value):
    s = InterpolatedString.create(input_string, parameters=parameters)
    assert s.eval(config, **{"kwargs": kwargs}) == expected_value
