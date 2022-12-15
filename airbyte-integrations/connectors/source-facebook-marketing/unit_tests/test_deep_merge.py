#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from copy import deepcopy

from source_facebook_marketing.streams.common import deep_merge


def test_return_new_object():
    """Should return new object, arguments should not be modified"""
    left = {
        "key_1": {
            "one": {"a", "b"},
            "two": "left_value",
        },
        "key_2": [1, 2],
    }
    right = {"key_1": {"two": "right_value", "three": [1, 2, 3]}, "key_2": [3]}
    expected_result = {"key_1": {"one": {"a", "b"}, "two": "right_value", "three": [1, 2, 3]}, "key_2": [1, 2, 3]}

    result = deep_merge(deepcopy(left), deepcopy(right))

    assert left == left
    assert right == right
    assert result == expected_result


def test_sets():
    left = {1, 2, 3}
    right = {4, 2, 1}
    result = deep_merge(left, right)

    assert result == {1, 2, 3, 4}


def test_lists():
    left = [1, 2, 3]
    right = [4, 2, 1]
    result = deep_merge(left, right)

    assert result == [1, 2, 3, 4, 2, 1]
