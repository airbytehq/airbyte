#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from typing import List, Set

import dpath.util
import yaml
from dagster import MetadataValue, Output, asset
from metadata_service.models.generated.ConnectorRegistryV0 import ConnectorRegistryV0

GROUP_NAME = "specs_secrets_mask"

# HELPERS


def get_secrets_properties_from_registry_entry(registry_entry: dict) -> List[str]:
    """Traverse a registry entry to spot properties in a spec that have the "airbyte_secret" field set to true.

    This function assumes all the properties have a "type" field that we can use to find all the nested properties in a spec.


    Args:
        registry_entry (dict): An entry in the registry with a spec field.

    Returns:
        List[str]: List of property names marked as airbyte_secret.
    """
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
def all_specs_secrets(persisted_oss_registry: ConnectorRegistryV0, persisted_cloud_registry: ConnectorRegistryV0) -> Set[str]:
    oss_registry_from_metadata_dict = persisted_oss_registry.dict()
    cloud_registry_from_metadata_dict = persisted_cloud_registry.dict()

    all_secret_properties = []
    all_entries = (
        oss_registry_from_metadata_dict["sources"]
        + cloud_registry_from_metadata_dict["sources"]
        + oss_registry_from_metadata_dict["destinations"]
        + cloud_registry_from_metadata_dict["destinations"]
    )
    for registry_entry in all_entries:
        all_secret_properties += get_secrets_properties_from_registry_entry(registry_entry)
    return set(all_secret_properties)


@asset(required_resource_keys={"registry_directory_manager"}, group_name=GROUP_NAME)
def specs_secrets_mask_yaml(context, all_specs_secrets: Set[str]) -> Output:
    yaml_string = yaml.dump({"properties": list(all_specs_secrets)})
    registry_directory_manager = context.resources.registry_directory_manager
    file_handle = registry_directory_manager.write_data(yaml_string.encode(), ext="yaml", key="specs_secrets_mask")
    metadata = {
        "preview": yaml_string,
        "gcs_path": MetadataValue.url(file_handle.gcs_path),
    }
    return Output(metadata=metadata, value=file_handle)
