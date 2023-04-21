import pandas as pd
from dagster import MetadataValue, Output, asset
from typing import List
from orchestrator.templates.render import render_connector_registry_report_markdown, render_connector_registry_locations_html

GROUP_NAME = "registry_reports"
OSS_SUFFIX = "_oss"
CLOUD_SUFFIX = "_cloud"

# HELPERS

# TODO choose a damn case
def get_github_url(docker_repo_name, github_connector_folders):
    if not isinstance(docker_repo_name, str):
        return None

    connector_name = docker_repo_name.replace("airbyte/", "")
    if connector_name in github_connector_folders:
        return f"https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/{connector_name}"
    else:
        return None

def docker_image_different(row):
    docker_image_oss = row["dockerRepository_oss"]
    docker_image_cloud = row["dockerRepository_cloud"]
    docker_image_version_oss = row["dockerImageTag_oss"]
    docker_image_version_cloud = row["dockerImageTag_cloud"]
    if docker_image_oss == docker_image_cloud and docker_image_version_oss == docker_image_version_cloud:
        return False
    else:
        return True


def icon_image_html(icon):
    github_org_project = "airbytehq/airbyte"
    github_icon_base = f"https://raw.githubusercontent.com/{github_org_project}/master/airbyte-config-oss/init-oss/src/main/resources/icons"
    icon_size = "30"
    icon_link = f'<img src="{github_icon_base}/{icon}" height="{icon_size}" height="{icon_size}"/>' if icon else "x"
    return icon_link;

    # github_code_base = f"https://github.com/{github_org_project}/tree/master/airbyte-integrations/connectors"
    # name = definition.get("name")
    # code_name = definition.get("dockerRepository").split("/")[1]
    # icon = definition.get("icon", "")
    # icon_link = f'<img alt="{name} icon" src="{github_icon_base}/{icon}" height="{icon_size}" height="{icon_size}"/>' if icon else "x"
    # docker_image = f"{definition.get('dockerRepository')}:{definition.get('dockerImageTag')}"
    # release_stage = definition.get("releaseStage", "unknown")
    # documentation_url = definition.get("documentationUrl", "")
    # doc_link = f"[docs]({documentation_url})" if documentation_url else "missing"

    # # We are trying to build a string like connectors/destination/mysql. We need to determine if this
    # # is a source or destination, lower-case, and then append back some stuff
    # issues_label = (
    #     f"connectors/{'source' if 'source-' in code_name else 'destination'}/"
    #     f"{code_name.replace('source-', '').replace('destination-', '')}"
    # )
    # issues_link = f"[{issues_label}](https://github.com/{github_org_project}/issues?q=is:open+is:issue+label:{issues_label})"
    # # https://github.com/airbytehq/airbyte/issues?q=is:open+is:issue+label:connectors/destination/mysql
    # code_link = f"[{code_name}]({github_code_base}/{code_name})"
    # id = f"<small>`{definition.get(type.lower() + 'DefinitionId')}`</small>"


def augment_and_normalize_connector_dataframes(
    cloud_df: pd.DataFrame, oss_df: pd.DataFrame, primaryKey: str, connector_type: str, github_connector_folders: List[str]
):
    """
    Normalize the cloud and oss connector dataframes and merge them into a single dataframe.
    Augment the dataframe with additional columns that indicate if the connector is in the cloud registry, oss registry, and if the metadata is valid.
    """

    # Add a column 'is_cloud' to indicate if an image/version pair is in the cloud registry
    cloud_df["is_cloud"] = True

    # Add a column 'is_oss' to indicate if an image/version pair is in the oss registry
    oss_df["is_oss"] = True

    # composite_key = [primaryKey, "dockerRepository", "dockerImageTag"]

    # Merge the two registries on the 'image' and 'version' columns
    total_registry = pd.merge(oss_df, cloud_df, how="outer", suffixes=(OSS_SUFFIX, CLOUD_SUFFIX), on=primaryKey)

    # remove duplicates from the merged dataframe
    total_registry = total_registry.drop_duplicates(subset=primaryKey, keep="first")

    # Replace NaN values in the 'is_cloud' and 'is_oss' columns with False
    total_registry[["is_cloud", "is_oss"]] = total_registry[["is_cloud", "is_oss"]].fillna(False)

    # registry_with_metadata = pd.merge(
    #     total_registry,
    #     valid_metadata_report_dataframe[["definitionId", "is_metadata_valid"]],
    #     left_on=primaryKey,
    #     right_on="definitionId",
    #     how="left",
    # )

    # merge with cached_specs on dockerRepository and dockerImageTag
    # cached_specs["is_spec_cached"] = True
    # merged_registry = pd.merge(
    #     total_registry,
    #     cached_specs,
    #     left_on=["dockerRepository", "dockerImageTag"],
    #     right_on=["docker_repository", "docker_image_tag"],
    #     how="left",
    # )

    # Set connectorType to 'source' or 'destination'
    total_registry["connector_type"] = connector_type


    # Set github url to the connector's folder in the github repo
    # To do this we need to parse the 'dockerRepository_oss' column to get the connector name
    # Its important to note that the 'dockerRepository_oss' column is only present if the connector is in the oss registry
    # And that dockerRepository_oss needs to have "airbyte/" stripped from the beginning of the string before it can match the github folder name
    # If the connector is not in the oss registry, then the 'dockerRepository_oss' column will be NaN
    # In this case, we will set the github url to be None
    total_registry["github_url"] = total_registry["dockerRepository_oss"].apply(
        lambda x: get_github_url(x, github_connector_folders)
    )


    total_registry["docker_image_different"] = total_registry.apply(docker_image_different, axis=1)

    # Rename column primaryKey to 'definitionId'
    total_registry.rename(columns={primaryKey: "definitionId"}, inplace=True)

    return total_registry


# ASSETS


# @asset(required_resource_keys={"registry_report_directory_manager"}, group_name=GROUP_NAME)
# def connector_registry_location_html(context, all_destinations_dataframe, all_sources_dataframe):
#     """
#     Generate an HTML report of the connector registry locations.
#     """

#     columns_to_show = [
#         "dockerRepository",
#         "dockerImageTag",
#         "is_oss",
#         "is_cloud",
#         "is_source_controlled",
#         "is_spec_cached",
#     ]

#     # convert true and false to checkmarks and x's
#     all_sources_dataframe.replace({True: "✅", False: "❌"}, inplace=True)
#     all_destinations_dataframe.replace({True: "✅", False: "❌"}, inplace=True)

#     html = render_connector_registry_locations_html(
#         destinations_table=all_destinations_dataframe[columns_to_show].to_html(),
#         sources_table=all_sources_dataframe[columns_to_show].to_html(),
#     )

#     registry_report_directory_manager = context.resources.registry_report_directory_manager
#     file_handle = registry_report_directory_manager.write_data(html.encode(), ext="html", key="connector_registry_locations")

#     metadata = {
#         "preview": html,
#         "gcs_path": MetadataValue.url(file_handle.gcs_path),
#     }

#     return Output(metadata=metadata, value=file_handle)


# @asset(required_resource_keys={"registry_report_directory_manager"}, group_name=GROUP_NAME)
# def connector_registry_location_markdown(context, all_destinations_dataframe, all_sources_dataframe):
#     """
#     Generate a markdown report of the connector registry locations.
#     """

#     columns_to_show = [
#         "dockerRepository",
#         "dockerImageTag",
#         "is_oss",
#         "is_cloud",
#         "is_source_controlled",
#         "is_spec_cached",
#     ]

#     # convert true and false to checkmarks and x's
#     all_sources_dataframe.replace({True: "✅", False: "❌"}, inplace=True)
#     all_destinations_dataframe.replace({True: "✅", False: "❌"}, inplace=True)

#     markdown = render_connector_registry_locations_markdown(
#         destinations_markdown=all_destinations_dataframe[columns_to_show].to_markdown(),
#         sources_markdown=all_sources_dataframe[columns_to_show].to_markdown(),
#     )

#     registry_report_directory_manager = context.resources.registry_report_directory_manager
#     file_handle = registry_report_directory_manager.write_data(markdown.encode(), ext="md", key="connector_registry_locations")

#     metadata = {
#         "preview": MetadataValue.md(markdown),
#         "gcs_path": MetadataValue.url(file_handle.gcs_path),
#     }
#     return Output(metadata=metadata, value=file_handle)


@asset(group_name=GROUP_NAME)
def all_sources_dataframe(
    cloud_sources_dataframe, oss_sources_dataframe, github_connector_folders
) -> pd.DataFrame:
    """
    Merge the cloud and oss sources registries into a single dataframe.
    """

    return augment_and_normalize_connector_dataframes(
        cloud_df=cloud_sources_dataframe,
        oss_df=oss_sources_dataframe,
        primaryKey="sourceDefinitionId",
        connector_type="source",
        github_connector_folders=github_connector_folders,
    )


@asset(group_name=GROUP_NAME)
def all_destinations_dataframe(
    cloud_destinations_dataframe, oss_destinations_dataframe, github_connector_folders
) -> pd.DataFrame:
    """
    Merge the cloud and oss destinations registries into a single dataframe.
    """

    return augment_and_normalize_connector_dataframes(
        cloud_df=cloud_destinations_dataframe,
        oss_df=oss_destinations_dataframe,
        primaryKey="destinationDefinitionId",
        connector_type="destination",
        github_connector_folders=github_connector_folders,
    )

@asset(required_resource_keys={"registry_report_directory_manager", "metadata_file_directory"}, group_name=GROUP_NAME)
def connector_registry_report(context, all_destinations_dataframe, all_sources_dataframe):
    """
    TODO
    """

    columns_to_show = [
        "definitionId",
        "name_oss",
        "icon_oss",
        "github_url",
        "releaseStage_oss",
        "documentationUrl_oss",
        "connector_type",
        "dockerRepository_oss",
        "dockerImageTag_oss",
        "dockerRepository_cloud",
        "dockerImageTag_cloud",
        "is_oss",
        "is_cloud",
        "docker_image_different",

        # "is_source_controlled",
        # "is_spec_cached",

        # build_status_badge
        # Do they match??
        # CDK version
        # issues
        # repo
        # source
    ]

    # convert true and false to checkmarks and x's
    all_sources_dataframe.replace({True: "✅", False: "❌"}, inplace=True)
    all_destinations_dataframe.replace({True: "✅", False: "❌"}, inplace=True)

    markdown = render_connector_registry_report_markdown(
        destinations_markdown=all_destinations_dataframe[columns_to_show].to_markdown(),
        sources_markdown=all_sources_dataframe[columns_to_show].to_markdown(),
    )

    html_formatters = {
        "icon_oss": icon_image_html,
    }

    html_string = render_connector_registry_locations_html(
        destinations_table=all_destinations_dataframe[columns_to_show].to_html(columns=columns_to_show, col_space="16rem" formatters=html_formatters, escape=False, classes="styled-table", na_rep="None", render_links=True),
        sources_table=all_sources_dataframe[columns_to_show].to_html(columns=columns_to_show, col_space="16rem" formatters=html_formatters, escape=False, classes="styled-table", na_rep="None", render_links=True),
    )

    registry_report_directory_manager = context.resources.registry_report_directory_manager
    metadata_file_directory = context.resources.metadata_file_directory
    # file_handle = registry_report_directory_manager.write_data(markdown.encode(), ext="md", key="connector_registry_report")
    # file_handle = registry_report_directory_manager.write_data(all_destinations_dataframe.to_json().encode(), ext="json", key="connector_registry_report")


    file_handle = metadata_file_directory.write_data(html_string.encode(), ext="html", key="connector_registry_report")

    metadata = {
        "preview": MetadataValue.md(markdown),
        # "preview2": MetadataValue.json(all_destinations_dataframe.to_json()),
        "gcs_path": MetadataValue.path(file_handle.path),
    }
    return Output(metadata=metadata, value=file_handle)

