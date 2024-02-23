#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import dpath.util
import pytest
from airbyte_cdk.sources.declarative.interpolation.interpolated_nested_mapping import InterpolatedNestedMapping


@pytest.mark.parametrize(
    "test_name, path, expected_value",
    [
        ("test_field_value", "nested/field", "value"),
        ("test_number", "nested/number", 100),
        ("test_interpolated_number", "nested/nested_array/1/value", 5),
        ("test_interpolated_boolean", "nested/nested_array/2/value", True),
        ("test_field_to_interpolate_from_config", "nested/config_value", "VALUE_FROM_CONFIG"),
        ("test_field_to_interpolate_from_kwargs", "nested/kwargs_value", "VALUE_FROM_KWARGS"),
        ("test_field_to_interpolate_from_parameters", "nested/parameters_value", "VALUE_FROM_PARAMETERS"),
        ("test_key_is_interpolated", "nested/nested_array/0/key", "VALUE"),
    ],
)
def test(test_name, path, expected_value):
    d = {
        "nested": {
            "field": "value",
            "number": 100,
            "nested_array": [
                {"{{ parameters.k }}": "VALUE"},
                {"value": "{{ config['num_value'] | int + 2 }}"},
                {"value": "{{ True }}"},
            ],
            "config_value": "{{ config['c'] }}",
            "parameters_value": "{{ parameters['b'] }}",
            "kwargs_value": "{{ kwargs['a'] }}",
        }
    }

    config = {"c": "VALUE_FROM_CONFIG", "num_value": 3}
    kwargs = {"a": "VALUE_FROM_KWARGS"}
    mapping = InterpolatedNestedMapping(mapping=d, parameters={"b": "VALUE_FROM_PARAMETERS", "k": "key"})

    interpolated = mapping.eval(config, **{"kwargs": kwargs})

    assert dpath.util.get(interpolated, path) == expected_value
