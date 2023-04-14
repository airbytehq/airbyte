#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from typing import List, Set

import dpath.util
import yaml
from dagster import asset

GROUP_NAME = "specs_secrets_mask"

# HELPERS


def get_secrets_properties_from_registry_entry(registry_entry: dict) -> List[str]:
    secret_properties = []
    spec_properties = registry_entry["spec"]["connectionSpecification"].get("properties")
    if spec_properties is None:
        return []
    for type_path, _ in dpath.util.search(spec_properties, "**/type", yielded=True):
        absolute_path = f"/{type_path}"
        if "/" in type_path:
            property_path, _ = absolute_path.rsplit(sep="/", maxsplit=1)
        else:
            property_path = absolute_path
        property_definition = dpath.util.get(spec_properties, property_path)
        marked_as_secret = property_definition.get("airbyte_secret", False)
        if marked_as_secret:
            secret_properties.append(property_path.split("/")[-1])
    return secret_properties


# ASSETS


@asset(group_name=GROUP_NAME)
def all_specs_secrets(oss_catalog_from_metadata_and_spec: dict, cloud_catalog_from_metadata_and_spec: dict) -> Set[str]:
    all_secret_properties = []
    all_entries = (
        oss_catalog_from_metadata_and_spec["sources"]
        + cloud_catalog_from_metadata_and_spec["sources"]
        + oss_catalog_from_metadata_and_spec["destinations"]
        + cloud_catalog_from_metadata_and_spec["destinations"]
    )
    for registry_entry in all_entries:
        all_secret_properties += get_secrets_properties_from_registry_entry(registry_entry)
    return set(all_secret_properties)


@asset(group_name=GROUP_NAME)
def specs_secrets_mask_yaml(all_specs_secrets: Set[str]) -> str:
    return yaml.dump({"properties": list(all_specs_secrets)})
