#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, List, Mapping

from airbyte_cdk.sources import Source
from airbyte_cdk.utils.mapping_utils import all_key_pairs_dot_notation, get_value_by_dot_notation


def get_secrets(source: Source, config: Mapping[str, Any], logger: logging.Logger) -> List[Any]:
    """
    Get a list of secrets from the source config based on the source specification
    """
    flattened_key_values = all_key_pairs_dot_notation(source.spec(logger).connectionSpecification.get("properties", {}))
    secret_key_names = [
        ".".join(key.split(".")[:1]) for key, value in flattened_key_values.items() if value and key.endswith("airbyte_secret")
    ]
    return [str(get_value_by_dot_notation(config, key)) for key in secret_key_names if config.get(key)]


class AirbyteSecretHelper:
    _secrets: List[str] = []

    @classmethod
    def update_secrets(cls, secrets: List[str]):
        """Update the list of secrets to be replaced"""
        cls._secrets = secrets

    @classmethod
    def filter_secrets(cls, string: str) -> str:
        """Filter secrets from a string by replacing them with ****"""
        for secret in cls._secrets:
            string = string.replace(secret, "****")
        return string
