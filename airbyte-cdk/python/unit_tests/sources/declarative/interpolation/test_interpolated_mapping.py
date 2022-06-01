#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.sources.declarative.interpolation.interpolated_mapping import InterpolatedMapping


def test():
    d = {
        "field": "value",
        "number": 100,
        "field_to_interpolate_from_config": "{{ config['c'] }}",
        "field_to_interpolate_from_kwargs": "{{ kwargs['a'] }}",
    }
    config = {"c": "VALUE_FROM_CONFIG"}
    kwargs = {"a": "VALUE_FROM_KWARGS"}
    mapping = InterpolatedMapping(d)

    interpolated = mapping.eval(config, **{"kwargs": kwargs})

    assert interpolated["field"] == "value"
    assert interpolated["number"] == 100
    assert interpolated["field_to_interpolate_from_config"] == "VALUE_FROM_CONFIG"
    assert interpolated["field_to_interpolate_from_kwargs"] == "VALUE_FROM_KWARGS"
