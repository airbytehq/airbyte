#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.sources.declarative.interpolation.interpolated_mapping import InterpolatedMapping


@pytest.mark.parametrize(
    "test_name, key, expected_value",
    [
        ("test_field_value", "field", "value"),
        ("test_number", "number", 100),
        ("test_field_to_interpolate_from_config", "field_to_interpolate_from_config", "VALUE_FROM_CONFIG"),
        ("test_field_to_interpolate_from_kwargs", "field_to_interpolate_from_kwargs", "VALUE_FROM_KWARGS"),
        ("test_field_to_interpolate_from_parameters", "field_to_interpolate_from_parameters", "VALUE_FROM_PARAMETERS"),
        ("test_key_is_interpolated", "key", "VALUE"),
    ],
)
def test(test_name, key, expected_value):
    d = {
        "field": "value",
        "number": 100,
        "field_to_interpolate_from_config": "{{ config['c'] }}",
        "field_to_interpolate_from_kwargs": "{{ kwargs['a'] }}",
        "field_to_interpolate_from_parameters": "{{ parameters['b'] }}",
        "{{ parameters.k }}": "VALUE",
    }
    config = {"c": "VALUE_FROM_CONFIG"}
    kwargs = {"a": "VALUE_FROM_KWARGS"}
    mapping = InterpolatedMapping(mapping=d, parameters={"b": "VALUE_FROM_PARAMETERS", "k": "key"})

    interpolated = mapping.eval(config, **{"kwargs": kwargs})

    assert interpolated[key] == expected_value
