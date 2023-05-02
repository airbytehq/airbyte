#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import json

import pandas as pd
from dagster import asset, OpExecutionContext


from orchestrator.utils.dagster_helpers import OutputDataFrame, output_dataframe


from metadata_service.models.generated.ConnectorRegistryV0 import ConnectorRegistryV0


GROUP_NAME = "legacy_registry"


@asset(group_name=GROUP_NAME)
def legacy_cloud_sources_dataframe(legacy_cloud_registry_dict: dict) -> OutputDataFrame:
    sources = legacy_cloud_registry_dict["sources"]
    return output_dataframe(pd.DataFrame(sources))


@asset(group_name=GROUP_NAME)
def legacy_oss_sources_dataframe(legacy_oss_registry_dict: dict) -> OutputDataFrame:
    sources = legacy_oss_registry_dict["sources"]
    return output_dataframe(pd.DataFrame(sources))


@asset(group_name=GROUP_NAME)
def legacy_cloud_destinations_dataframe(legacy_cloud_registry_dict: dict) -> OutputDataFrame:
    destinations = legacy_cloud_registry_dict["destinations"]
    return output_dataframe(pd.DataFrame(destinations))


@asset(group_name=GROUP_NAME)
def legacy_oss_destinations_dataframe(legacy_oss_registry_dict: dict) -> OutputDataFrame:
    destinations = legacy_oss_registry_dict["destinations"]
    return output_dataframe(pd.DataFrame(destinations))


@asset(required_resource_keys={"legacy_cloud_registry_gcs_blob"}, group_name=GROUP_NAME)
def legacy_cloud_registry(legacy_cloud_registry_dict: dict) -> ConnectorRegistryV0:
    return ConnectorRegistryV0.parse_obj(legacy_cloud_registry_dict)


@asset(required_resource_keys={"legacy_oss_registry_gcs_blob"}, group_name=GROUP_NAME)
def legacy_oss_registry(legacy_oss_registry_dict: dict) -> ConnectorRegistryV0:
    return ConnectorRegistryV0.parse_obj(legacy_oss_registry_dict)


@asset(required_resource_keys={"legacy_cloud_registry_gcs_blob"}, group_name=GROUP_NAME)
def legacy_cloud_registry_dict(context: OpExecutionContext) -> dict:
    oss_registry_file = context.resources.legacy_cloud_registry_gcs_blob
    json_string = oss_registry_file.download_as_string().decode("utf-8")
    oss_registry_dict = json.loads(json_string)
    return oss_registry_dict


@asset(required_resource_keys={"legacy_oss_registry_gcs_blob"}, group_name=GROUP_NAME)
def legacy_oss_registry_dict(context: OpExecutionContext) -> dict:
    oss_registry_file = context.resources.legacy_oss_registry_gcs_blob
    json_string = oss_registry_file.download_as_string().decode("utf-8")
    oss_registry_dict = json.loads(json_string)
    return oss_registry_dict
