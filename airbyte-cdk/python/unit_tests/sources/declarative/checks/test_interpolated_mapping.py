#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.sources.declarative.interpolation.interpolated_mapping import InterpolatedMapping


def test():
    d = {
        "field": "value",
        "field_to_interpolate_from_config": "{{ config['c'] }}",
        "field_to_interpolate_from_kwargs": "{{ kwargs['a'] }}",
        "a_field": "{{ value_passed_directly }}",
    }
    config = {"c": "VALUE_FROM_CONFIG"}
    kwargs = {"a": "VALUE_FROM_KWARGS"}
    mapping = InterpolatedMapping(d)

    value_passed_directly = "ABC"
    interpolated = mapping.eval(config, **{"kwargs": kwargs}, value_passed_directly=value_passed_directly)

    assert interpolated["field"] == "value"
    assert interpolated["field_to_interpolate_from_config"] == "VALUE_FROM_CONFIG"
    assert interpolated["field_to_interpolate_from_kwargs"] == "VALUE_FROM_KWARGS"
    assert interpolated["a_field"] == value_passed_directly
