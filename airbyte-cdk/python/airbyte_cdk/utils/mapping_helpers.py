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
    combined_mapping = {}
    unique_keys = set()
    string_mappings = 0
    string_mapping_value = None

    for part in mappings:
        if part is None:
            continue
        if isinstance(part, str):
            string_mappings += 1
            string_mapping_value = part
            if string_mappings > 1:
                raise ValueError("Cannot combine multiple string options")
        else:
            for key in part:
                if key in unique_keys:
                    raise ValueError(f"Duplicate keys found: {key}")
                combined_mapping[key] = part[key]
                unique_keys.add(key)

    if string_mappings == 1:
        if combined_mapping:
            raise ValueError("Cannot combine multiple options if one is a string")
        return string_mapping_value

    return combined_mapping
