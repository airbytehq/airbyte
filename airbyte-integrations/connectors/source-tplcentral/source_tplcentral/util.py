#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping


def deep_map(function, collection):
    if isinstance(collection, list):
        return list(map(lambda val: deep_map(function, val), collection))

    collection = function(collection)
    for key, val in collection.items():
        if isinstance(val, dict):
            collection[key] = deep_map(function, val)
        elif isinstance(val, list):
            collection[key] = deep_map(function, val)
        else:
            collection[key] = val
    return collection


def normalize(collection):
    return deep_map(_normalizer, collection)


def _normalizer(dictionary):
    out = {}
    for key, val in dictionary.items():
        if not key == "_links":
            out[key] = val
    return out


def deep_get(mapping: Mapping[str, Any], key: str) -> Any:
    key = key.split(".")
    while len(key):
        mapping = mapping[key.pop(0)]
    return mapping
