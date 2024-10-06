#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Optional, Set, Union


def combine_mappings(mappings: List[Optional[Union[Mapping[str, Any], str]]]) -> Union[Mapping[str, Any], str]:
    """
    Combine multiple mappings into a single mapping. If any of the mappings are a string, return
    that string. Raise errors in the following cases:
    * If there are duplicate keys across mappings
    * If there are multiple string mappings
    * If there are multiple mappings containing keys and one of them is a string
    """
    all_keys: List[Set[str]] = []
    for part in mappings:
        if part is None:
            continue
        keys = set(part.keys()) if not isinstance(part, str) else set()
        all_keys.append(keys)

    string_options = sum(isinstance(mapping, str) for mapping in mappings)
    # If more than one mapping is a string, raise a ValueError
    if string_options > 1:
        raise ValueError("Cannot combine multiple string options")

    if string_options == 1 and sum(len(keys) for keys in all_keys) > 0:
        raise ValueError("Cannot combine multiple options if one is a string")

    # If any mapping is a string, return it
    for mapping in mappings:
        if isinstance(mapping, str):
            return mapping

    # If there are duplicate keys across mappings, raise a ValueError
    intersection = set().union(*all_keys)
    if len(intersection) < sum(len(keys) for keys in all_keys):
        raise ValueError(f"Duplicate keys found: {intersection}")

    # Return the combined mappings
    return {key: value for mapping in mappings if mapping for key, value in mapping.items()}  # type: ignore # mapping can't be string here
