# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
import json
import logging
from dataclasses import dataclass
from os import scandir
from typing import Any, Callable, List

import pandas as pd
from google.cloud import storage

from metadata_service.constants import (
    CONNECTORS_PATH,
    GITHUB_REPO_NAME,
    METADATA_CDN_BASE_URL,
    REGISTRIES_FOLDER,
    get_public_url_for_gcs_file,
)
from metadata_service.helpers.gcs import get_gcs_storage_client
from metadata_service.models.generated import ConnectorRegistryV0
from metadata_service.models.transform import to_json_sanitized_dict
from metadata_service.templates.render import (
    ColumnInfo,
    dataframe_to_table_html,
    icon_image_html,
    internal_level_html,
    render_connector_registry_locations_html,
    simple_link_html,
    test_badge_html,
)

logger = logging.getLogger(__name__)

REPORT_FILE_NAME = "connector_registry_report"
CONNECTOR_TEST_SUMMARY_FOLDER = "test_summary"
REPORT_FOLDER = "generated_reports"
OSS_SUFFIX = "_oss"
CLOUD_SUFFIX = "_cloud"

# 🖼️ Dataframe Columns


def _github_url(docker_repo_name: str, github_connector_folders: List[str]) -> str | None:
    if not isinstance(docker_repo_name, str):
        return None

    connector_name = docker_repo_name.replace("airbyte/", "")
    if connector_name in github_connector_folders:
        return f"https://github.com/{GITHUB_REPO_NAME}/blob/master/airbyte-integrations/connectors/{connector_name}"
    else:
        return None


def _issue_url(row: pd.DataFrame) -> str | None:
    docker_repo = row["dockerRepository_oss"]
    if not isinstance(docker_repo, str):
        print(f"no docker repo: {row}")
        return None

    code_name = docker_repo.split("/")[1]
    issues_label = (
        f"connectors/{'source' if 'source-' in code_name else 'destination'}/"
        f"{code_name.replace('source-', '').replace('destination-', '')}"
    )
    return f"https://github.com/{GITHUB_REPO_NAME}/issues?q=is:open+is:issue+label:{issues_label}"


def _merge_docker_repo_and_version(row: pd.DataFrame, suffix: str) -> str | None:
    docker_repo = row[f"dockerRepository{suffix}"]
    docker_version = row[f"dockerImageTag{suffix}"]

    if not isinstance(docker_repo, str):
        return None

    return f"{docker_repo}:{docker_version}"


def _test_summary_url(row: pd.DataFrame) -> str | None:
    docker_repo_name = row["dockerRepository_oss"]
    if not isinstance(docker_repo_name, str):
        return None

    connector = docker_repo_name.replace("airbyte/", "")

    path = f"{REPORT_FOLDER}/{CONNECTOR_TEST_SUMMARY_FOLDER}/{connector}"

    # get_public_url_for_gcs_file ignores the bucket name if a CDN URL is provided
    return get_public_url_for_gcs_file("unused", path, METADATA_CDN_BASE_URL)


def _ab_internal_sl(row: pd.DataFrame) -> int | None:
    ab_internal = row.get("ab_internal_oss")
    if not isinstance(ab_internal, dict) or "sl" not in ab_internal:
        return None
    sl = ab_internal["sl"]
    if not isinstance(sl, int):
        raise Exception(f"expected sl to be string; got {type(sl)} ({sl})")
    return sl


def _ab_internal_ql(row: pd.DataFrame) -> int | None:
    ab_internal = row.get("ab_internal_oss")
    if not isinstance(ab_internal, dict) or "ql" not in ab_internal:
        return None
    ql = ab_internal["ql"]
    if not isinstance(ql, int):
        raise Exception(f"expected ql to be string; got {type(ql)} ({ql})")
    return ql


# 📊 Dataframe Augmentation


def _augment_and_normalize_connector_dataframes(
    cloud_df: pd.DataFrame, oss_df: pd.DataFrame, primary_key: str, connector_type: str, github_connector_folders: List[str]
) -> pd.DataFrame:
    """
    Normalize the cloud and oss connector dataframes and merge them into a single dataframe.
    Augment the dataframe with additional columns that indicate if the connector is in the cloud registry, oss registry, and if the metadata is valid.
    """

    # Add a column 'is_cloud' to indicate if an image/version pair is in the cloud registry
    cloud_df["is_cloud"] = True

    # Add a column 'is_oss' to indicate if an image/version pair is in the oss registry
    oss_df["is_oss"] = True

    # Merge the two registries on the 'image' and 'version' columns
    total_registry = pd.merge(oss_df, cloud_df, how="outer", suffixes=(OSS_SUFFIX, CLOUD_SUFFIX), on=primary_key)

    # remove duplicates from the merged dataframe
    total_registry = total_registry.drop_duplicates(subset=primary_key, keep="first")

    # Replace NaN values in the 'is_cloud' and 'is_oss' columns with False
    total_registry[["is_cloud", "is_oss"]] = total_registry[["is_cloud", "is_oss"]].fillna(False)

    # Set connectorType to 'source' or 'destination'
    total_registry["connector_type"] = connector_type

    total_registry["github_url"] = total_registry["dockerRepository_oss"].apply(lambda x: _github_url(x, github_connector_folders))

    total_registry["issue_url"] = total_registry.apply(_issue_url, axis=1)
    total_registry["test_summary_url"] = total_registry.apply(_test_summary_url, axis=1)

    # Show Internal Fields
    total_registry["ab_internal_ql"] = total_registry.apply(_ab_internal_ql, axis=1)
    total_registry["ab_internal_sl"] = total_registry.apply(_ab_internal_sl, axis=1)

    # Merge docker repo and version into separate columns
    total_registry["docker_image_oss"] = total_registry.apply(lambda x: _merge_docker_repo_and_version(x, OSS_SUFFIX), axis=1)
    total_registry["docker_image_cloud"] = total_registry.apply(lambda x: _merge_docker_repo_and_version(x, CLOUD_SUFFIX), axis=1)
    total_registry["docker_images_match"] = total_registry["docker_image_oss"] == total_registry["docker_image_cloud"]

    # Rename column primary_key to 'definitionId'
    total_registry.rename(columns={primary_key: "definitionId"}, inplace=True)

    return total_registry


# ASSETS


def _cloud_sources_dataframe(latest_cloud_registry: ConnectorRegistryV0) -> pd.DataFrame:
    latest_cloud_registry_dict = to_json_sanitized_dict(latest_cloud_registry)
    sources = latest_cloud_registry_dict["sources"]
    return pd.DataFrame(sources)


def _oss_sources_dataframe(latest_oss_registry: ConnectorRegistryV0) -> pd.DataFrame:
    latest_oss_registry_dict = to_json_sanitized_dict(latest_oss_registry)
    sources = latest_oss_registry_dict["sources"]
    return pd.DataFrame(sources)


def _cloud_destinations_dataframe(latest_cloud_registry: ConnectorRegistryV0) -> pd.DataFrame:
    latest_cloud_registry_dict = to_json_sanitized_dict(latest_cloud_registry)
    destinations = latest_cloud_registry_dict["destinations"]
    return pd.DataFrame(destinations)


def _oss_destinations_dataframe(latest_oss_registry: ConnectorRegistryV0) -> pd.DataFrame:
    latest_oss_registry_dict = to_json_sanitized_dict(latest_oss_registry)
    destinations = latest_oss_registry_dict["destinations"]
    return pd.DataFrame(destinations)


def _all_sources_dataframe(cloud_sources_dataframe, oss_sources_dataframe, github_connector_folders) -> pd.DataFrame:
    """
    Merge the cloud and oss sources registries into a single dataframe.
    """

    return _augment_and_normalize_connector_dataframes(
        cloud_df=cloud_sources_dataframe,
        oss_df=oss_sources_dataframe,
        primary_key="sourceDefinitionId",
        connector_type="source",
        github_connector_folders=github_connector_folders,
    )


def _all_destinations_dataframe(cloud_destinations_dataframe, oss_destinations_dataframe, github_connector_folders) -> pd.DataFrame:
    """
    Merge the cloud and oss destinations registries into a single dataframe.
    """

    return _augment_and_normalize_connector_dataframes(
        cloud_df=cloud_destinations_dataframe,
        oss_df=oss_destinations_dataframe,
        primary_key="destinationDefinitionId",
        connector_type="destination",
        github_connector_folders=github_connector_folders,
    )


def _github_connector_folders() -> List[str]:
    """
    Return a list of all the folders in the github connectors directory.
    """
    folder_names = [item.name for item in scandir(CONNECTORS_PATH) if item.is_dir()]
    return folder_names


def _load_registry(bucket: storage.Bucket, filename: str) -> ConnectorRegistryV0:
    latest_oss_registry_gcs_blob = bucket.blob(f"{REGISTRIES_FOLDER}/{filename}")
    json_string = latest_oss_registry_gcs_blob.download_as_string().decode("utf-8")
    latest_cloud_registry_dict = json.loads(json_string)
    return ConnectorRegistryV0.parse_obj(latest_cloud_registry_dict)


def generate_and_persist_registry_report(bucket_name: str) -> None:
    """Generate and persist the registry report to GCS.

    Args:
        bucket_name (str): The name of the bucket to persist the registry report to.

    Returns:
        None
    """
    client = get_gcs_storage_client()
    bucket = client.bucket(bucket_name)

    github_connector_folders = _github_connector_folders()

    latest_cloud_registry = _load_registry(bucket, "cloud_registry.json")
    latest_oss_registry = _load_registry(bucket, "oss_registry.json")

    all_destinations_dataframe = _all_destinations_dataframe(
        _cloud_destinations_dataframe(latest_cloud_registry),
        _oss_destinations_dataframe(latest_oss_registry),
        github_connector_folders,
    )
    all_sources_dataframe = _all_sources_dataframe(
        _cloud_sources_dataframe(latest_cloud_registry),
        _oss_sources_dataframe(latest_oss_registry),
        github_connector_folders,
    )

    all_connectors_dataframe = pd.concat([all_destinations_dataframe, all_sources_dataframe])
    all_connectors_dataframe.reset_index(inplace=True)

    columns_to_show: List[ColumnInfo] = [
        {
            "column": "name_oss",
            "title": "Connector Name",
        },
        {
            "column": "definitionId",
            "title": "Definition Id",
        },
        {
            "column": "iconUrl_oss",
            "title": "Icon",
            "formatter": icon_image_html,
        },
        {
            "column": "connector_type",
            "title": "Connector Type",
        },
        {
            "column": "releaseStage_oss",
            "title": "Release Stage",
        },
        {
            "column": "supportLevel_oss",
            "title": "Support Level",
        },
        {
            "column": "ab_internal_sl",
            "title": "Internal SL",
            "formatter": internal_level_html,
        },
        {
            "column": "ab_internal_ql",
            "title": "Internal QL",
            "formatter": internal_level_html,
        },
        {
            "column": "test_summary_url",
            "title": "Build Status",
            "formatter": test_badge_html,
        },
        {
            "column": "is_oss",
            "title": "OSS",
        },
        {
            "column": "is_cloud",
            "title": "Cloud",
        },
        {
            "column": "docker_image_oss",
            "title": "Docker Image OSS",
        },
        {
            "column": "docker_image_cloud",
            "title": "Docker Image Cloud",
        },
        {
            "column": "docker_images_match",
            "title": "OSS and Cloud Docker Images Match",
        },
        {
            "column": "github_url",
            "title": "Source",
            "formatter": simple_link_html,
        },
        {
            "column": "documentationUrl_oss",
            "title": "Docs",
            "formatter": simple_link_html,
        },
        {
            "column": "issue_url",
            "title": "Issues",
            "formatter": simple_link_html,
        },
    ]

    html_string = render_connector_registry_locations_html(
        destinations_table_html=dataframe_to_table_html(all_destinations_dataframe, columns_to_show),
        sources_table_html=dataframe_to_table_html(all_sources_dataframe, columns_to_show),
    )

    json_string = all_connectors_dataframe.to_json(orient="records")

    json_file_blob = bucket.blob(f"{REPORT_FOLDER}/{REPORT_FILE_NAME}.json")
    html_file_blob = bucket.blob(f"{REPORT_FOLDER}/{REPORT_FILE_NAME}.html")
    try:
        logger.info(f"Uploading registry report to GCS: {json_file_blob.name}")
        json_file_blob.upload_from_string(json_string.encode())
        html_file_blob.upload_from_string(html_string.encode())
    except Exception as e:
        logger.error(f"Error uploading registry report to GCS: {e}")
        raise e
