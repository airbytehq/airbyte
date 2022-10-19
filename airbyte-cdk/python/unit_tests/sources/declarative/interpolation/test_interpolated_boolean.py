#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean

config = {
    "parent": {"key_with_true": True},
    "string_key": "compare_me",
    "zero_value": 0,
    "empty_array": [],
    "non_empty_array": [1],
    "empty_dict": {},
    "empty_tuple": (),
}


@pytest.mark.parametrize(
    "test_name, template, expected_result",
    [
        ("test_interpolated_true_value", "{{ config['parent']['key_with_true'] }}", True),
        ("test_interpolated_true_comparison", "{{ config['string_key'] == \"compare_me\" }}", True),
        ("test_interpolated_false_condition", "{{ config['string_key'] == \"witness_me\" }}", False),
        ("test_path_has_value_returns_true", "{{ config['string_key'] }}", True),
        ("test_missing_key_defaults_to_false", "{{ path_to_nowhere }}", False),
        ("test_zero_is_false", "{{ config['zero_value'] }}", False),
        ("test_empty_array_is_false", "{{ config['empty_array'] }}", False),
        ("test_empty_dict_is_false", "{{ config['empty_dict'] }}", False),
        ("test_empty_tuple_is_false", "{{ config['empty_tuple'] }}", False),
        ("test_lowercase_false", '{{ "false" }}', False),
        ("test_False", "{{ False }}", False),
        ("test_True", "{{ True }}", True),
        ("test_value_in_array", "{{ 1 in config['non_empty_array'] }}", True),
        ("test_value_not_in_array", "{{ 2 in config['non_empty_array'] }}", False),
        ("test_interpolation_using_options", "{{ options['from_options'] == \"come_find_me\" }}", True),
    ],
)
def test_interpolated_boolean(test_name, template, expected_result):
    interpolated_bool = InterpolatedBoolean(condition=template, options={"from_options": "come_find_me"})
    assert interpolated_bool.eval(config) == expected_result
