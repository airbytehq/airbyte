#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping

import dpath


def get_secret_paths(spec: Mapping[str, Any]) -> List[List[str]]:
    paths = []

    def traverse_schema(schema_item: Any, path: List[str]) -> None:
        """
        schema_item can be any property or value in the originally input jsonschema, depending on how far down the recursion stack we go
        path is the path to that schema item in the original input
        for example if we have the input {'password': {'type': 'string', 'airbyte_secret': True}} then the arguments will evolve
        as follows:
        schema_item=<whole_object>, path=[]
        schema_item={'type': 'string', 'airbyte_secret': True}, path=['password']
        schema_item='string', path=['password', 'type']
        schema_item=True, path=['password', 'airbyte_secret']
        """
        if isinstance(schema_item, dict):
            for k, v in schema_item.items():
                traverse_schema(v, [*path, k])
        elif isinstance(schema_item, list):
            for i in schema_item:
                traverse_schema(i, path)
        else:
            if path[-1] == "airbyte_secret" and schema_item is True:
                filtered_path = [p for p in path[:-1] if p not in ["properties", "oneOf"]]
                paths.append(filtered_path)

    traverse_schema(spec, [])
    return paths


def get_secrets(
    connection_specification: Mapping[str, Any], config: Mapping[str, Any]
) -> List[Any]:
    """
    Get a list of secret values from the source config based on the source specification
    :type connection_specification: the connection_specification field of an AirbyteSpecification i.e the JSONSchema definition
    """
    secret_paths = get_secret_paths(connection_specification.get("properties", {}))
    result = []
    for path in secret_paths:
        try:
            result.append(dpath.get(config, path))  # type: ignore  # dpath expect MutableMapping but doesn't need it
        except KeyError:
            # Since we try to get paths to all known secrets in the spec, in the case of oneOfs, some secret fields may not be present
            # In that case, a KeyError is thrown. This is expected behavior.
            pass
    return result


__SECRETS_FROM_CONFIG: List[str] = []


def update_secrets(secrets: List[str]) -> None:
    """Update the list of secrets to be replaced"""
    global __SECRETS_FROM_CONFIG
    __SECRETS_FROM_CONFIG = secrets


def add_to_secrets(secret: str) -> None:
    """Add to the list of secrets to be replaced"""
    global __SECRETS_FROM_CONFIG
    __SECRETS_FROM_CONFIG.append(secret)


def filter_secrets(string: str) -> str:
    """Filter secrets from a string by replacing them with ****"""
    # TODO this should perform a maximal match for each secret. if "x" and "xk" are both secret values, and this method is called twice on
    #  the input "xk", then depending on call order it might only obfuscate "*k". This is a bug.
    for secret in __SECRETS_FROM_CONFIG:
        if secret:
            string = string.replace(str(secret), "****")
    return string
