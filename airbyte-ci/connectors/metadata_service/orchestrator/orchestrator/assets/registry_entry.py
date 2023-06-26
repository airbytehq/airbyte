import pandas as pd
import numpy as np
import os
from typing import List
from dagster import DynamicPartitionsDefinition, asset, OpExecutionContext
import yaml

from metadata_service.models.generated.ConnectorMetadataDefinitionV0 import ConnectorMetadataDefinitionV0
from metadata_service.constants import METADATA_FILE_NAME, ICON_FILE_NAME

from orchestrator.utils.object_helpers import are_values_equal, merge_values
from orchestrator.models.metadata import PartialMetadataDefinition, MetadataDefinition, LatestMetadataEntry
from orchestrator.config import get_public_url_for_gcs_file

from orchestrator.utils.dagster_helpers import OutputDataFrame, output_dataframe


GROUP_NAME = "registry_entry"

metadata_partitions_def = DynamicPartitionsDefinition(name="metadata")

@asset(required_resource_keys={"latest_metadata_file_blobs"}, group_name=GROUP_NAME, partitions_def=metadata_partitions_def)
def metadata_entry(context: OpExecutionContext) -> LatestMetadataEntry:
    etag = context.partition_key
    latest_metadata_file_blobs = context.resources.latest_metadata_file_blobs

    # find the blob with the matching etag
    matching_blob = next(
        (blob for blob in latest_metadata_file_blobs if blob.etag == etag), None
    )

    if not matching_blob:
        raise Exception(f"Could not find blob with etag {etag}")

    # read the matching_blob
    yaml_string = matching_blob.download_as_string().decode("utf-8")
    metadata_dict = yaml.safe_load(yaml_string)
    metadata_def = MetadataDefinition.parse_obj(metadata_dict)

    metadata_file_path = matching_blob.name
    icon_file_path = metadata_file_path.replace(METADATA_FILE_NAME, ICON_FILE_NAME)
    icon_blob = matching_blob.bucket.blob(icon_file_path)

    icon_url = (
        get_public_url_for_gcs_file(icon_blob.bucket.name, icon_blob.name, os.getenv("METADATA_CDN_BASE_URL"))
        if icon_blob.exists()
        else None
    )

    metadata_entry = LatestMetadataEntry(
        metadata_definition=metadata_def,
        icon_url=icon_url,
        bucket_name=matching_blob.bucket.name,
        file_path=metadata_file_path,
    )
    # import pdb; pdb.set_trace()
    return metadata_entry

@asset(group_name=GROUP_NAME, partitions_def=metadata_partitions_def)
def registry_entry(context: OpExecutionContext, metadata_entry: LatestMetadataEntry) -> OutputDataFrame:
    metadata_entry_df = pd.DataFrame(metadata_entry.dict())
    return output_dataframe(metadata_entry_df)

