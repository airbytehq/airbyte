#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from functools import reduce
from typing import Any, List, Mapping, Optional


def all_key_pairs_dot_notation(dict_obj: Mapping) -> Mapping[str, Any]:
    """
    Recursively iterate through a dictionary and return a dictionary of all key-value pairs in dot notation.
    keys are prefixed with the list of keys passed in as prefix.
    """

    def _all_key_pairs_dot_notation(_dict_obj: Mapping, prefix: List[str] = []) -> Mapping[str, Any]:
        for key, value in _dict_obj.items():
            if isinstance(value, dict):
                prefix.append(str(key))
                yield from _all_key_pairs_dot_notation(value, prefix)
                prefix.pop()
            else:
                prefix.append(str(key))
                yield ".".join(prefix), value
                prefix.pop()

    return {k: v for k, v in _all_key_pairs_dot_notation(dict_obj)}


def get_value_by_dot_notation(dict_obj: Mapping, key: str, default: Optional[Any] = ...) -> Any:
    """
    Return the value of a key in dot notation in a arbitrarily nested Mapping.
    dict_obj: Mapping
    key: str
    default: Any
    raises: KeyError if default is not provided and the key is not found
    ex.:
        dict_obj = {"nested": {"key": "value"}}
        get_value_by_dot_notation(dict_obj, "nested.key") == "value" -> True
    """

    return reduce(lambda d, key_name: d[key_name] if default is ... else d.get(key_name, default), key.split("."), dict_obj)
