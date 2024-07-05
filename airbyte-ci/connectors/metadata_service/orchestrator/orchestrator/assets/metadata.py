#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os
from typing import List

import numpy as np
import pandas as pd
import yaml
from dagster import OpExecutionContext, Output, asset
from metadata_service.constants import ICON_FILE_NAME, METADATA_FILE_NAME
from metadata_service.models.generated.ConnectorMetadataDefinitionV0 import ConnectorMetadataDefinitionV0
from orchestrator.config import get_public_url_for_gcs_file
from orchestrator.logging import sentry
from orchestrator.models.metadata import LatestMetadataEntry, MetadataDefinition, PartialMetadataDefinition
from orchestrator.utils.object_helpers import are_values_equal, merge_values

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


# ASSETS


@asset(required_resource_keys={"latest_metadata_file_blobs"}, group_name=GROUP_NAME)
@sentry.instrument_asset_op
def metadata_definitions(context: OpExecutionContext) -> List[LatestMetadataEntry]:
    latest_metadata_file_blobs = context.resources.latest_metadata_file_blobs

    metadata_entries = []
    for blob in latest_metadata_file_blobs:
        yaml_string = blob.download_as_string().decode("utf-8")
        metadata_dict = yaml.safe_load(yaml_string)
        metadata_def = MetadataDefinition.parse_obj(metadata_dict)

        metadata_file_path = blob.name
        icon_file_path = metadata_file_path.replace(METADATA_FILE_NAME, ICON_FILE_NAME)
        icon_blob = blob.bucket.blob(icon_file_path)

        icon_url = (
            get_public_url_for_gcs_file(icon_blob.bucket.name, icon_blob.name, os.getenv("METADATA_CDN_BASE_URL"))
            if icon_blob.exists()
            else None
        )

        metadata_entry = LatestMetadataEntry(
            metadata_definition=metadata_def,
            icon_url=icon_url,
            last_modified=blob.last_modified,
            etag=blob.etag,
            file_path=blob.name,
            bucket_name=blob.bucket.name,
        )
        metadata_entries.append(metadata_entry)

    return metadata_entries
