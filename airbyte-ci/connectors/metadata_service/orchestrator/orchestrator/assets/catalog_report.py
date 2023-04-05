import pandas as pd
from dagster import MetadataValue, Output, asset

from orchestrator.templates.render import render_connector_catalog_locations_html, render_connector_catalog_locations_markdown

GROUP_NAME = "catalog_reports"

# HELPERS


def augment_and_normalize_connector_dataframes(
    cloud_df, oss_df, primaryKey, connector_type, valid_metadata_report_dataframe, github_connector_folders, cached_specs
):
    """
    Normalize the cloud and oss connector dataframes and merge them into a single dataframe.
    Augment the dataframe with additional columns that indicate if the connector is in the cloud catalog, oss catalog, and if the metadata is valid.
    """

    # Add a column 'is_cloud' to indicate if an image/version pair is in the cloud catalog
    cloud_df["is_cloud"] = True

    # Add a column 'is_oss' to indicate if an image/version pair is in the oss catalog
    oss_df["is_oss"] = True

    composite_key = [primaryKey, "dockerRepository", "dockerImageTag"]

    # Merge the two catalogs on the 'image' and 'version' columns, keeping only the unique pairs
    total_catalog = pd.merge(cloud_df, oss_df, how="outer", on=composite_key).drop_duplicates(subset=composite_key)

    # Replace NaN values in the 'is_cloud' and 'is_oss' columns with False
    total_catalog[["is_cloud", "is_oss"]] = total_catalog[["is_cloud", "is_oss"]].fillna(False)

    catalog_with_metadata = pd.merge(
        total_catalog,
        valid_metadata_report_dataframe[["definitionId", "is_metadata_valid"]],
        left_on=primaryKey,
        right_on="definitionId",
        how="left",
    )

    # merge with cached_specs on dockerRepository and dockerImageTag
    cached_specs["is_spec_cached"] = True
    merged_catalog = pd.merge(
        catalog_with_metadata,
        cached_specs,
        left_on=["dockerRepository", "dockerImageTag"],
        right_on=["docker_repository", "docker_image_tag"],
        how="left",
    )

    # Set connectorType to 'source' or 'destination'
    merged_catalog["connector_type"] = connector_type
    merged_catalog["is_source_controlled"] = merged_catalog["dockerRepository"].apply(
        lambda x: x.lstrip("airbyte/") in github_connector_folders
    )

    return merged_catalog


# ASSETS


@asset(required_resource_keys={"catalog_report_directory_manager"}, group_name=GROUP_NAME)
def connector_catalog_location_html(context, all_destinations_dataframe, all_sources_dataframe):
    """
    Generate an HTML report of the connector catalog locations.
    """

    columns_to_show = [
        "dockerRepository",
        "dockerImageTag",
        "is_oss",
        "is_cloud",
        "is_source_controlled",
        "is_spec_cached",
        "is_metadata_valid",
    ]

    # convert true and false to checkmarks and x's
    all_sources_dataframe.replace({True: "✅", False: "❌"}, inplace=True)
    all_destinations_dataframe.replace({True: "✅", False: "❌"}, inplace=True)

    html = render_connector_catalog_locations_html(
        destinations_table=all_destinations_dataframe[columns_to_show].to_html(),
        sources_table=all_sources_dataframe[columns_to_show].to_html(),
    )

    catalog_report_directory_manager = context.resources.catalog_report_directory_manager
    file_handle = catalog_report_directory_manager.write_data(html.encode(), ext="html", key="connector_catalog_locations")

    metadata = {
        "preview": html,
        "gcs_path": MetadataValue.url(file_handle.gcs_path),
    }

    return Output(metadata=metadata, value=file_handle)


@asset(required_resource_keys={"catalog_report_directory_manager"}, group_name=GROUP_NAME)
def connector_catalog_location_markdown(context, all_destinations_dataframe, all_sources_dataframe):
    """
    Generate a markdown report of the connector catalog locations.
    """

    columns_to_show = [
        "dockerRepository",
        "dockerImageTag",
        "is_oss",
        "is_cloud",
        "is_source_controlled",
        "is_spec_cached",
        "is_metadata_valid",
    ]

    # convert true and false to checkmarks and x's
    all_sources_dataframe.replace({True: "✅", False: "❌"}, inplace=True)
    all_destinations_dataframe.replace({True: "✅", False: "❌"}, inplace=True)

    markdown = render_connector_catalog_locations_markdown(
        destinations_markdown=all_destinations_dataframe[columns_to_show].to_markdown(),
        sources_markdown=all_sources_dataframe[columns_to_show].to_markdown(),
    )

    catalog_report_directory_manager = context.resources.catalog_report_directory_manager
    file_handle = catalog_report_directory_manager.write_data(markdown.encode(), ext="md", key="connector_catalog_locations")

    metadata = {
        "preview": MetadataValue.md(markdown),
        "gcs_path": MetadataValue.url(file_handle.gcs_path),
    }
    return Output(metadata=metadata, value=file_handle)


@asset(group_name=GROUP_NAME)
def all_destinations_dataframe(
    cloud_destinations_dataframe, oss_destinations_dataframe, github_connector_folders, valid_metadata_report_dataframe, cached_specs
) -> pd.DataFrame:
    """
    Merge the cloud and oss destinations catalogs into a single dataframe.
    """

    return augment_and_normalize_connector_dataframes(
        cloud_df=cloud_destinations_dataframe,
        oss_df=oss_destinations_dataframe,
        primaryKey="destinationDefinitionId",
        connector_type="destination",
        valid_metadata_report_dataframe=valid_metadata_report_dataframe,
        github_connector_folders=github_connector_folders,
        cached_specs=cached_specs,
    )


@asset(group_name=GROUP_NAME)
def all_sources_dataframe(
    cloud_sources_dataframe, oss_sources_dataframe, github_connector_folders, valid_metadata_report_dataframe, cached_specs
) -> pd.DataFrame:
    """
    Merge the cloud and oss source catalogs into a single dataframe.
    """
    return augment_and_normalize_connector_dataframes(
        cloud_df=cloud_sources_dataframe,
        oss_df=oss_sources_dataframe,
        primaryKey="sourceDefinitionId",
        connector_type="source",
        valid_metadata_report_dataframe=valid_metadata_report_dataframe,
        github_connector_folders=github_connector_folders,
        cached_specs=cached_specs,
    )
