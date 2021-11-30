from typing import List, Mapping, Any

from airbyte_cdk.sources import Source
from airbyte_cdk.utils.mapping_utils import (
    all_key_pairs_dot_notation,
    get_value_by_dot_notation,
)


def get_secrets(source: Source, config: Mapping[str, Any]) -> List[Any]:
    """
    Get a list of secrets from the source config based on the source specification
    """
    flattened_key_values = all_key_pairs_dot_notation(
        source.spec().connectionSpecification.get("properties", {})
    )
    secret_key_names = [
        ".".join(key.split(".")[:1])
        for key, value in flattened_key_values.items()
        if value and key.endswith(f"airbyte_secret")
    ]
    result = [
        str(get_value_by_dot_notation(config, key))
        for key in secret_key_names
        if config.get(key)
    ]
    return result
