#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import copy
from typing import Any, Dict, List, Mapping, Optional, Union

from airbyte_cdk.sources.declarative.requesters.request_option import (
    RequestOption,
    RequestOptionType,
)
from airbyte_cdk.sources.types import Config, StreamSlice, StreamState


def _merge_mappings(
    target: Dict[str, Any],
    source: Mapping[str, Any],
    path: Optional[List[str]] = None,
    allow_same_value_merge: bool = False,
) -> None:
    """
    Recursively merge two dictionaries, raising an error if there are any conflicts.
    For body_json requests (allow_same_value_merge=True), a conflict occurs only when the same path has different values.
    For other request types (allow_same_value_merge=False), any duplicate key is a conflict, regardless of value.

    Args:
        target: The dictionary to merge into
        source: The dictionary to merge from
        path: The current path in the nested structure (for error messages)
        allow_same_value_merge: Whether to allow merging the same value into the same key. Set to false by default, should only be true for body_json injections
    """
    path = path or []
    for key, source_value in source.items():
        current_path = path + [str(key)]

        if key in target:
            target_value = target[key]
            if isinstance(target_value, dict) and isinstance(source_value, dict):
                # Only body_json supports nested_structures
                if not allow_same_value_merge:
                    raise ValueError(
                        f"Request body collision, duplicate keys detected at key path: {'.'.join(current_path)}. Please ensure that all keys in the request are unique."
                    )
                # If both are dictionaries, recursively merge them
                _merge_mappings(target_value, source_value, current_path, allow_same_value_merge)

            elif not allow_same_value_merge or target_value != source_value:
                # If same key has different values, that's a conflict
                raise ValueError(
                    f"Request body collision, duplicate keys detected at key path: {'.'.join(current_path)}. Please ensure that all keys in the request are unique."
                )
        else:
            # No conflict, just copy the value (using deepcopy for nested structures)
            target[key] = copy.deepcopy(source_value)


def combine_mappings(
    mappings: List[Optional[Union[Mapping[str, Any], str]]],
    allow_same_value_merge: bool = False,
) -> Union[Mapping[str, Any], str]:
    """
    Combine multiple mappings into a single mapping.

    For body_json requests (allow_same_value_merge=True):
        - Supports nested structures (e.g., {"data": {"user": {"id": 1}}})
        - Allows duplicate keys if their values match
        - Raises error if same path has different values

    For other request types (allow_same_value_merge=False):
        - Only supports flat structures
        - Any duplicate key raises an error, regardless of value

    Args:
        mappings: List of mappings to combine
        allow_same_value_merge: Whether to allow duplicate keys with matching values.
                              Should only be True for body_json requests.

    Returns:
        A single mapping combining all inputs, or a string if there is exactly one
        string mapping and no other non-empty mappings.

    Raises:
        ValueError: If there are:
            - Multiple string mappings
            - Both a string mapping and non-empty dictionary mappings
            - Conflicting keys/paths based on allow_same_value_merge setting
    """
    if not mappings:
        return {}

    # Count how many string options we have, ignoring None values
    string_options = sum(isinstance(mapping, str) for mapping in mappings if mapping is not None)
    if string_options > 1:
        raise ValueError("Cannot combine multiple string options")

    # Filter out None values and empty mappings
    non_empty_mappings = [
        m for m in mappings if m is not None and not (isinstance(m, Mapping) and not m)
    ]

    # If there is only one string option and no other non-empty mappings, return it
    if string_options == 1:
        if len(non_empty_mappings) > 1:
            raise ValueError("Cannot combine multiple options if one is a string")
        return next(m for m in non_empty_mappings if isinstance(m, str))

    # Start with an empty result and merge each mapping into it
    result: Dict[str, Any] = {}
    for mapping in non_empty_mappings:
        if mapping and isinstance(mapping, Mapping):
            _merge_mappings(result, mapping, allow_same_value_merge=allow_same_value_merge)

    return result


def _validate_component_request_option_paths(
    config: Config, *request_options: Optional[RequestOption]
) -> None:
    """
    Validates that a component with multiple request options does not have conflicting paths.
    Uses dummy values for validation since actual values might not be available at init time.
    """
    grouped_options: Dict[RequestOptionType, List[RequestOption]] = {}
    for option in request_options:
        if option:
            grouped_options.setdefault(option.inject_into, []).append(option)

    for inject_type, options in grouped_options.items():
        if len(options) <= 1:
            continue

        option_dicts: List[Optional[Union[Mapping[str, Any], str]]] = []
        for i, option in enumerate(options):
            option_dict: Dict[str, Any] = {}
            # Use indexed dummy values to ensure we catch conflicts
            option.inject_into_request(option_dict, f"dummy_value_{i}", config)
            option_dicts.append(option_dict)

        try:
            combine_mappings(
                option_dicts, allow_same_value_merge=(inject_type == RequestOptionType.body_json)
            )
        except ValueError as error:
            raise ValueError(error)


def get_interpolation_context(
    stream_state: Optional[StreamState] = None,
    stream_slice: Optional[StreamSlice] = None,
    next_page_token: Optional[Mapping[str, Any]] = None,
) -> Mapping[str, Any]:
    return {
        "stream_slice": stream_slice,
        "next_page_token": next_page_token,
        # update the context with extra fields, if passed.
        **(
            stream_slice.extra_fields
            if stream_slice is not None and hasattr(stream_slice, "extra_fields")
            else {}
        ),
    }
