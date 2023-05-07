import pandas as pd
from dagster import MetadataValue, Output, asset
from typing import List
from orchestrator.templates.render import (
    render_connector_registry_locations_html,
    dataframe_to_table_html,
    simple_link_html,
    icon_image_html,
    test_badge_html,
    ColumnInfo,
)
from orchestrator.config import CONNECTOR_REPO_NAME, CONNECTORS_TEST_RESULT_BUCKET_URL

GROUP_NAME = "registry_reports"

OSS_SUFFIX = "_oss"
CLOUD_SUFFIX = "_cloud"

# 🖼️ Dataframe Columns


def github_url(docker_repo_name: str, github_connector_folders: List[str]) -> str:
    if not isinstance(docker_repo_name, str):
        return None

    connector_name = docker_repo_name.replace("airbyte/", "")
    if connector_name in github_connector_folders:
        return f"https://github.com/{CONNECTOR_REPO_NAME}/blob/master/airbyte-integrations/connectors/{connector_name}"
    else:
        return None


def icon_url(row: pd.DataFrame) -> str:
    icon_file_name = row["icon_oss"]
    if not isinstance(icon_file_name, str):
        return None

    github_icon_base = (
        f"https://raw.githubusercontent.com/{CONNECTOR_REPO_NAME}/master/airbyte-config-oss/init-oss/src/main/resources/icons"
    )
    return f"{github_icon_base}/{icon_file_name}"


def issue_url(row: pd.DataFrame) -> str:
    docker_repo = row["dockerRepository_oss"]
    if not isinstance(docker_repo, str):
        print(f"no docker repo: {row}")
        return None

    code_name = docker_repo.split("/")[1]
    issues_label = (
        f"connectors/{'source' if 'source-' in code_name else 'destination'}/"
        f"{code_name.replace('source-', '').replace('destination-', '')}"
    )
    return f"https://github.com/{CONNECTOR_REPO_NAME}/issues?q=is:open+is:issue+label:{issues_label}"


def merge_docker_repo_and_version(row: pd.DataFrame, suffix: str) -> str:
    docker_repo = row[f"dockerRepository{suffix}"]
    docker_version = row[f"dockerImageTag{suffix}"]

    if not isinstance(docker_repo, str):
        return None

    return f"{docker_repo}:{docker_version}"


def test_summary_url(row: pd.DataFrame) -> str:
    docker_repo_name = row["dockerRepository_oss"]
    if not isinstance(docker_repo_name, str):
        return None

    connector = docker_repo_name.replace("airbyte/", "")

    return f"{CONNECTORS_TEST_RESULT_BUCKET_URL}/tests/summary/connectors/{connector}"


# 📊 Dataframe Augmentation


def augment_and_normalize_connector_dataframes(
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

    total_registry["github_url"] = total_registry["dockerRepository_oss"].apply(lambda x: github_url(x, github_connector_folders))

    total_registry["issue_url"] = total_registry.apply(issue_url, axis=1)
    total_registry["test_summary_url"] = total_registry.apply(test_summary_url, axis=1)
    total_registry["icon_url"] = total_registry.apply(icon_url, axis=1)

    # Merge docker repo and version into separate columns
    total_registry["docker_image_oss"] = total_registry.apply(lambda x: merge_docker_repo_and_version(x, OSS_SUFFIX), axis=1)
    total_registry["docker_image_cloud"] = total_registry.apply(lambda x: merge_docker_repo_and_version(x, CLOUD_SUFFIX), axis=1)
    total_registry["docker_images_match"] = total_registry["docker_image_oss"] == total_registry["docker_image_cloud"]

    # Rename column primary_key to 'definitionId'
    total_registry.rename(columns={primary_key: "definitionId"}, inplace=True)

    return total_registry


# ASSETS

# TODO (ben): Update these assets to reference the new registry once deployed


@asset(group_name=GROUP_NAME)
def all_sources_dataframe(legacy_cloud_sources_dataframe, legacy_oss_sources_dataframe, github_connector_folders) -> pd.DataFrame:
    """
    Merge the cloud and oss sources registries into a single dataframe.
    """

    return augment_and_normalize_connector_dataframes(
        cloud_df=legacy_cloud_sources_dataframe,
        oss_df=legacy_oss_sources_dataframe,
        primary_key="sourceDefinitionId",
        connector_type="source",
        github_connector_folders=github_connector_folders,
    )


@asset(group_name=GROUP_NAME)
def all_destinations_dataframe(
    legacy_cloud_destinations_dataframe, legacy_oss_destinations_dataframe, github_connector_folders
) -> pd.DataFrame:
    """
    Merge the cloud and oss destinations registries into a single dataframe.
    """

    return augment_and_normalize_connector_dataframes(
        cloud_df=legacy_cloud_destinations_dataframe,
        oss_df=legacy_oss_destinations_dataframe,
        primary_key="destinationDefinitionId",
        connector_type="destination",
        github_connector_folders=github_connector_folders,
    )


@asset(required_resource_keys={"registry_report_directory_manager"}, group_name=GROUP_NAME)
def connector_registry_report(context, all_destinations_dataframe, all_sources_dataframe):
    """
    Generate a report of the connector registry.
    """

    report_file_name = "connector_registry_report"
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
            "column": "icon_url",
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

    registry_report_directory_manager = context.resources.registry_report_directory_manager

    json_file_handle = registry_report_directory_manager.write_data(json_string.encode(), ext="json", key=report_file_name)
    html_file_handle = registry_report_directory_manager.write_data(html_string.encode(), ext="html", key=report_file_name)

    metadata = {
        "first_10_preview": MetadataValue.md(all_connectors_dataframe.head(10).to_markdown()),
        "json": MetadataValue.json(json_string),
        "json_gcs_url": MetadataValue.url(json_file_handle.public_url),
        "html_gcs_url": MetadataValue.url(html_file_handle.public_url),
    }
    return Output(metadata=metadata, value=html_file_handle)
