#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from typing import List

import dpath.util

# from dagster import asset

GROUP_NAME = "specs_secrets_mask"

# HELPERS


def get_secrets_properties_from_registry_entry(registry_entry: dict) -> List[str]:
    secret_properties = []
    spec_properties = registry_entry["spec"]["connectionSpecification"]["properties"]
    for type_path, _ in dpath.util.search(spec_properties, "**/type", yielded=True):
        absolute_path = f"/{type_path}"
        property_path, _ = absolute_path.rsplit(sep="/", maxsplit=1)
        property_definition = dpath.util.get(spec_properties, property_path)
        marked_as_secret = property_definition.get("airbyte_secret", False)
        if marked_as_secret:
            secret_properties.append(property_path.split("/")[-1])
    return secret_properties


# ASSETS


# @asset(group_name=GROUP_NAME)
# def specs_secrets_mask(oss_catalog_from_metadata: dict) -> List[str]:
#     all_secret_properties = []
#     for registry_entry in oss_catalog_from_metadata["sources"] + oss_catalog_from_metadata["destinations"]:
#         all_secret_properties += get_secrets_properties_from_registry_entry(registry_entry)
#     return all_secret_properties
