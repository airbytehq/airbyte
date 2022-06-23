#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, List, Mapping

import dpath.util


def get_secret_paths(schema: Mapping[str, Any]) -> List[str]:
    paths = []

    def traverse_schema(schema: Any, path: List[str]):
        if isinstance(schema, dict):
            for k, v in schema.items():
                traverse_schema(v, [*path, k])
        elif isinstance(schema, list):
            for i in schema:
                traverse_schema(i, path)
        else:
            if path[-1] == "airbyte_secret" and schema is True:
                filtered_path = [p for p in path[:-1] if p not in ["properties", "oneOf"]]
                paths.append(filtered_path)

    traverse_schema(schema, [])
    return paths


def get_secrets(connection_specification: Mapping[str, Any], config: Mapping[str, Any], logger: logging.Logger) -> List[Any]:
    """
    Get a list of secret values from the source config based on the source specification
    :type connection_specification: the connection_specification field of an AirbyteSpecification i.e the JSONSchema definition
    """
    secret_paths = get_secret_paths(connection_specification.get("properties", {}))
    result = []
    for path in secret_paths:
        try:
            result.append(dpath.util.get(config, path))
        except KeyError:
            pass
    return result


__SECRETS_FROM_CONFIG: List[str] = []


def update_secrets(secrets: List[str]):
    """Update the list of secrets to be replaced"""
    global __SECRETS_FROM_CONFIG
    __SECRETS_FROM_CONFIG = secrets


def filter_secrets(string: str) -> str:
    """Filter secrets from a string by replacing them with ****"""
    # TODO this should perform a maximal match for each secret. if "x" and "xk" are both secret values, and this method is called twice on
    #  the input "xk", then depending on call order it might only obfuscate "*k". This is a bug.
    for secret in __SECRETS_FROM_CONFIG:
        string = string.replace(str(secret), "****")
    return string
