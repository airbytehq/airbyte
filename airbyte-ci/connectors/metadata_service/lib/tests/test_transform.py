#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pathlib

import yaml
from metadata_service.models import transform
from metadata_service.models.generated.ConnectorMetadataDefinitionV0 import ConnectorMetadataDefinitionV0


def get_all_dict_key_paths(dict_to_traverse, key_path=""):
    """Get all paths to keys in a dict.

    Args:
        dict_to_traverse (dict): A dict.

    Returns:
        list: List of paths to keys in the dict. e.g ["data.name", "data.version", "data.meta.url""]
    """
    if not isinstance(dict_to_traverse, dict):
        return [key_path]

    key_paths = []
    for key, value in dict_to_traverse.items():
        new_key_path = f"{key_path}.{key}" if key_path else key
        key_paths += get_all_dict_key_paths(value, new_key_path)

    return key_paths


def have_same_keys(dict1, dict2, omitted_keys=None):
    """Check if two dicts have the same keys, ignoring specified keys in the second dict.

    Args:
        dict1 (dict): A dict.
        dict2 (dict): A dict.
        omitted_keys (list, optional): List of keys to ignore in dict2.

    Returns:
        tuple: (bool, list) - True if the dicts have the same keys (considering omissions),
               and a list of keys that are different or omitted.
    """
    if omitted_keys is None:
        omitted_keys = []

    keys1 = set(get_all_dict_key_paths(dict1))
    keys2 = set(get_all_dict_key_paths(dict2))

    # Determine the difference in keys
    different_keys = list(keys1.symmetric_difference(keys2))

    # Remove omitted keys
    different_keys = [key for key in different_keys if key not in omitted_keys]

    return len(different_keys) == 0, different_keys


def test_transform_to_json_does_not_mutate_keys(valid_metadata_upload_files, valid_metadata_yaml_files):
    all_valid_metadata_files = valid_metadata_upload_files + valid_metadata_yaml_files

    fields_with_defaults = ["data.supportsRefreshes"]

    for file_path in all_valid_metadata_files:
        metadata_file_path = pathlib.Path(file_path)
        original_yaml_text = metadata_file_path.read_text()

        metadata_yaml_dict = yaml.safe_load(original_yaml_text)
        metadata = ConnectorMetadataDefinitionV0.parse_obj(metadata_yaml_dict)
        metadata_json_dict = transform.to_json_sanitized_dict(metadata)

        new_yaml_text = yaml.safe_dump(metadata_json_dict, sort_keys=False)
        new_yaml_dict = yaml.safe_load(new_yaml_text)

        # assert same keys in both dicts, deep compare, and that the values are the same
        is_same, different_keys = have_same_keys(metadata_yaml_dict, new_yaml_dict, fields_with_defaults)
        assert is_same, f"Different keys found: {different_keys}"
