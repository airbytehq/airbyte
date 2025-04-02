#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import pytest
from source_linkedin_ads.utils import update_specific_key


@pytest.mark.parametrize(
    "target_dict, target_key, target_value, condition_func, excluded_keys, expected_output",
    [
        (
            {"key1": "value1", "key2": "value2"},
            "key1",
            "new_value1",
            None,
            None,
            {"key1": "new_value1", "key2": "value2"},
        ),
        (
            {"key1": "value1", "key2": "value2"},
            "key1",
            "new_value1",
            None,
            ["key1"],
            {"key1": "value1", "key2": "value2"},
        ),
        (
            {"key1": "value1", "key2": "value2"},
            "key1",
            "new_value1",
            lambda x: x["key2"] == "value2",
            None,
            {"key1": "new_value1", "key2": "value2"},
        ),
        (
            {"outer_key": {"key1": "value1", "key2": "value2"}},
            "key1",
            "new_value1",
            None,
            None,
            {"outer_key": {"key1": "new_value1", "key2": "value2"}},
        ),
        (
            {"key_list": [{"key1": "value1"}, {"key1": "value2"}]},
            "key1",
            "new_value1",
            None,
            None,
            {"key_list": [{"key1": "new_value1"}, {"key1": "new_value1"}]},
        ),
        (
            {"outer_key": {"key1": "value1", "key2": "value2"}},
            "key1",
            "new_value1",
            None,
            ["key1"],
            {"outer_key": {"key1": "value1", "key2": "value2"}},
        ),
        (
            {"key_list": [{"key1": "value1"}, "string", {"key1": "value2"}]},
            "key1",
            "new_value1",
            None,
            None,
            {"key_list": [{"key1": "new_value1"}, "string", {"key1": "new_value1"}]},
        ),
    ],
    ids=[
        "simple_dictionary_update",
        "exclude_key_from_update",
        "condition_function_update",
        "nested_dictionary_update",
        "list_of_dictionaries_update",
        "excluded_key_in_nested_dict",
        "nested_list_with_mixed_types",
    ],
)
def test_update_specific_key(target_dict, target_key, target_value, condition_func, excluded_keys, expected_output):
    result = update_specific_key(target_dict, target_key, target_value, condition_func, excluded_keys)
    assert result == expected_output
