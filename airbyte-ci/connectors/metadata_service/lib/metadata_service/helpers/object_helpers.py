#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


import copy
from enum import EnumMeta


def deep_copy_params(to_call):
    def f(*args, **kwargs):
        return to_call(*copy.deepcopy(args), **copy.deepcopy(kwargs))

    return f


class CaseInsensitiveKeys(EnumMeta):
    """A metaclass for creating enums with case-insensitive keys."""

    def __getitem__(cls, item):
        try:
            return super().__getitem__(item)
        except Exception:
            for key in cls._member_map_:
                if key.casefold() == item.casefold():
                    return super().__getitem__(key)


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
