# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
"""Hashing utils for PyAirbyte."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping


HASH_SEED = "PyAirbyte:"
"""Additional seed for randomizing one-way hashed strings."""


def one_way_hash(
    obj: Mapping | list | object,
    /,
) -> str:
    """Return a one-way hash of the given string.

    To ensure a unique domain of hashes, we prepend a seed to the string before hashing.
    """
    string_to_hash: str
    if isinstance(obj, Mapping):
        # Recursively sort and convert nested dictionaries to tuples of key-value pairs
        string_to_hash = str(sorted((k, one_way_hash(v)) for k, v in obj.items()))

    elif isinstance(obj, list):
        # Recursively hash elements of the list
        string_to_hash = str([one_way_hash(item) for item in obj])

    else:
        # Convert the object to a string
        string_to_hash = str(obj)

    return hashlib.sha256((HASH_SEED + str(string_to_hash)).encode()).hexdigest()
