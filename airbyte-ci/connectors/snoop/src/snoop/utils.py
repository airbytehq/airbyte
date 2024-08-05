# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
import hashlib
import os

import yaml


def sort_dict_keys(d: dict) -> dict:
    if isinstance(d, dict):
        sorted_dict = {}
        for key in sorted(d.keys()):
            sorted_dict[key] = sort_dict_keys(d[key])
        return sorted_dict
    else:
        return d


def sanitize_stream_name(stream_name: str) -> str:
    return stream_name.replace("/", "_").replace(" ", "_").lower()


def hash_value(value):
    """Returns the SHA-256 hash of the given value."""
    if isinstance(value, str):
        value = value.encode("utf-8")
    elif not isinstance(value, bytes):
        value = str(value).encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def hash_dict_values(d):
    def recurse_dict(d):
        for key, value in d.items():
            if isinstance(value, dict):
                d[key] = recurse_dict(value)
            else:
                d[key] = hash_value(value)
        return d

    if not isinstance(d, dict):
        raise ValueError("Input must be a dictionary.")

    return recurse_dict(d)

def get_connector_metadata() -> dict:
    with open(os.environ["PATH_TO_METADATA"], "r") as metadata_file:
        return yaml.safe_load(metadata_file)