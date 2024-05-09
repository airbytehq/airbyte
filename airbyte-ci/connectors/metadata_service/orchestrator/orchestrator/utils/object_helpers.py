#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
import json
from typing import TypeVar

import mergedeep
from deepdiff import DeepDiff

T = TypeVar("T")


def are_values_equal(value_1: any, value_2: any) -> bool:
    if isinstance(value_1, dict) and isinstance(value_2, dict):
        diff = DeepDiff(value_1, value_2, ignore_order=True)
        return len(diff) == 0
    else:
        return value_1 == value_2


def merge_values(old_value: T, new_value: T) -> T:
    if isinstance(old_value, dict) and isinstance(new_value, dict):
        merged = old_value.copy()
        mergedeep.merge(merged, new_value)
        return merged
    else:
        return new_value


def deep_copy_params(to_call):
    def f(*args, **kwargs):
        return to_call(*copy.deepcopy(args), **copy.deepcopy(kwargs))

    return f


def default_none_to_dict(value, key, obj):
    """Set the value of a key in a dictionary to an empty dictionary if the value is None.

    Useful with pydash's set_with function.

    e.g. set_with(obj, key, value, default_none_to_dict)

    For more information, see https://github.com/dgilland/pydash/issues/122

    Args:
        value: The value to check.
        key: The key to set in the dictionary.
        obj: The dictionary to set the key in.
    """
    if obj is None:
        return

    if value is None:
        obj[key] = {}
