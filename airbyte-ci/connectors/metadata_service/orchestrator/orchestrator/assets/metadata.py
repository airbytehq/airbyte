import pandas as pd
import numpy as np
from typing import List
from dagster import Output, asset, OpExecutionContext
import yaml

from metadata_service.models.generated.ConnectorMetadataDefinitionV0 import ConnectorMetadataDefinitionV0

from orchestrator.utils.object_helpers import are_values_equal, merge_values
from orchestrator.utils.dagster_helpers import OutputDataFrame, output_dataframe
from orchestrator.models.metadata import PartialMetadataDefinition, MetadataDefinition

GROUP_NAME = "metadata"


# HELPERS

OSS_SUFFIX = "_oss"
CLOUD_SUFFIX = "_cloud"


def get_primary_registry_suffix(merged_df):
    """
    Returns the suffix for the primary registry and the secondary registry.
    The primary registry is the one that is used for the final metadata.
    The secondary registry is the one that is used for overrides.

    This is nessesary because we have connectors that are only in the cloud registry and vice versa.
    """
    cloud_only = merged_df["_merge"] == "right_only"
    primary_suffix = CLOUD_SUFFIX if cloud_only else OSS_SUFFIX
    secondary_suffix = OSS_SUFFIX if cloud_only else CLOUD_SUFFIX
    return primary_suffix, secondary_suffix


def get_field_with_fallback(merged_df, field):
    """
    Returns the value of the field from the primary registry.
    If the field is not present in the primary registry, the value from the secondary registry is returned.
    """

    primary_suffix, secondary_suffix = get_primary_registry_suffix(merged_df)

    primary_field = field + primary_suffix
    secondary_field = field + secondary_suffix

    secondary_value = merged_df.get(secondary_field)
    return merged_df.get(primary_field, default=secondary_value)


def compute_registry_overrides(merged_df):
    """
    Returns the registry overrides section for the metadata file.
    """
    cloud_only = merged_df["_merge"] == "right_only"
    oss_only = merged_df["_merge"] == "left_only"

    registries = {
        "oss": {
            "enabled": not cloud_only,
        },
        "cloud": {
            "enabled": not oss_only,
        },
    }

    if cloud_only or oss_only:
        return registries

    allowed_overrides = [
        "name",
        "dockerRepository",
        "dockerImageTag",
        "supportsDbt",
        "supportsNormalization",
        "license",
        "supportUrl",
        "connectorSubtype",
        "allowedHosts",
        "normalizationConfig",
        "suggestedStreams",
        "resourceRequirements",
    ]

    # find the difference between the two registries
    for override_col in allowed_overrides:
        oss_col = override_col + OSS_SUFFIX
        cloud_col = override_col + CLOUD_SUFFIX

        cloud_value = merged_df.get(cloud_col)
        oss_value = merged_df.get(oss_col)

        # if the columns are different, add the cloud value to the overrides
        if cloud_value and not are_values_equal(oss_value, cloud_value):
            registries["cloud"][override_col] = merge_values(oss_value, cloud_value)

    return registries


def merge_into_metadata_definitions(
    id_field: str, connector_type: str, oss_connector_df: pd.DataFrame, cloud_connector_df: pd.DataFrame
) -> List[PartialMetadataDefinition]:
    """Merges the OSS and Cloud connector metadata into a single metadata definition.

    Args:
        id_field (str): The field that uniquely identifies a connector.
        connector_type (str): The type of connector (source or destination).
        oss_connector_df (pd.DataFrame): The dataframe containing the related OSS connector in the registry.
        cloud_connector_df (pd.DataFrame): The dataframe containing the related Cloud connector in the registry.

    Returns:
        pd.Series: The merged metadata definition.
    """
    merged_connectors = pd.merge(
        oss_connector_df, cloud_connector_df, on=id_field, how="outer", suffixes=(OSS_SUFFIX, CLOUD_SUFFIX), indicator=True
    )

    # Replace numpy nan values with None
    sanitized_connectors = merged_connectors.replace([np.nan], [None])

    def build_metadata(connector_registry_entry: dict) -> PartialMetadataDefinition:
        """Builds the metadata definition for a single connector.

        Args:
            connector_registry_entry (dict): The merged connector metadata from the existing json registries.

        Returns:
            PartialMetadataDefinition: The final metadata definition.
        """
        raw_data = {
            "name": get_field_with_fallback(connector_registry_entry, "name"),
            "definitionId": connector_registry_entry[id_field],
            "connectorType": connector_type,
            "dockerRepository": get_field_with_fallback(connector_registry_entry, "dockerRepository"),
            "githubIssueLabel": get_field_with_fallback(connector_registry_entry, "dockerRepository").replace("airbyte/", ""),
            "dockerImageTag": get_field_with_fallback(connector_registry_entry, "dockerImageTag"),
            "icon": get_field_with_fallback(connector_registry_entry, "icon"),
            "supportUrl": get_field_with_fallback(connector_registry_entry, "documentationUrl"),
            "connectorSubtype": get_field_with_fallback(connector_registry_entry, "sourceType"),
            "releaseStage": get_field_with_fallback(connector_registry_entry, "releaseStage"),
            "license": "MIT",
            "supportsDbt": get_field_with_fallback(connector_registry_entry, "supportsDbt"),
            "supportsNormalization": get_field_with_fallback(connector_registry_entry, "supportsNormalization"),
            "allowedHosts": get_field_with_fallback(connector_registry_entry, "allowedHosts"),
            "normalizationConfig": get_field_with_fallback(connector_registry_entry, "normalizationConfig"),
            "suggestedStreams": get_field_with_fallback(connector_registry_entry, "suggestedStreams"),
            "resourceRequirements": get_field_with_fallback(connector_registry_entry, "resourceRequirements"),
        }

        # remove none values
        data = {k: v for k, v in raw_data.items() if v is not None}

        metadata = {"metadataSpecVersion": "1.0", "data": data}

        registries = compute_registry_overrides(connector_registry_entry)
        metadata["data"]["registries"] = registries

        return PartialMetadataDefinition.construct(**metadata)

    metadata_list = [build_metadata(connector_registry_entry) for _, connector_registry_entry in sanitized_connectors.iterrows()]

    return metadata_list


def validate_metadata(metadata: PartialMetadataDefinition) -> tuple[bool, str]:
    try:
        ConnectorMetadataDefinitionV0.parse_obj(metadata)
        return True, None
    except Exception as e:
        return False, str(e)


# ASSETS


@asset(group_name=GROUP_NAME)
def valid_metadata_report_dataframe(overrode_metadata_definitions: List[PartialMetadataDefinition]) -> OutputDataFrame:
    """
    Validates the metadata definitions and returns a dataframe with the results
    """

    result = []

    for metadata in overrode_metadata_definitions:
        valid, error_msg = metadata.is_valid
        result.append(
            {
                "definitionId": metadata["data"]["definitionId"],
                "name": metadata["data"]["name"],
                "dockerRepository": metadata["data"]["dockerRepository"],
                "is_metadata_valid": valid,
                "error_msg": error_msg,
            }
        )

    result_df = pd.DataFrame(result)

    return output_dataframe(result_df)


@asset(group_name=GROUP_NAME)
def legacy_registry_derived_metadata_definitions(
    legacy_cloud_sources_dataframe, legacy_cloud_destinations_dataframe, legacy_oss_sources_dataframe, legacy_oss_destinations_dataframe
) -> Output[List[PartialMetadataDefinition]]:
    sources_metadata_list = merge_into_metadata_definitions(
        "sourceDefinitionId", "source", legacy_oss_sources_dataframe, legacy_cloud_sources_dataframe
    )
    destinations_metadata_list = merge_into_metadata_definitions(
        "destinationDefinitionId", "destination", legacy_oss_destinations_dataframe, legacy_cloud_destinations_dataframe
    )
    all_definitions = sources_metadata_list + destinations_metadata_list
    return Output(all_definitions, metadata={"count": len(all_definitions)})


@asset(required_resource_keys={"latest_metadata_file_blobs"}, group_name=GROUP_NAME)
def metadata_definitions(context: OpExecutionContext) -> List[MetadataDefinition]:
    latest_metadata_file_blobs = context.resources.latest_metadata_file_blobs

    metadata_definitions = []
    for blob in latest_metadata_file_blobs:
        yaml_string = blob.download_as_string().decode("utf-8")
        metadata_dict = yaml.safe_load(yaml_string)
        metadata_def = MetadataDefinition.parse_obj(metadata_dict)
        metadata_definitions.append(metadata_def)

    return metadata_definitions
