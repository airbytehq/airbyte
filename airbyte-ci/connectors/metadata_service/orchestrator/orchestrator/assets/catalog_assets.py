import pandas as pd
import json
import requests
from ..utils.dagster_helpers import OutputDataFrame
from dagster import MetadataValue, Output, asset, OpExecutionContext

from ..templates.render import render_connector_catalog_locations_html, render_connector_catalog_locations_markdown

# HELPERS

GROUP_NAME = "catalog"


# TODO
# - add  column for whether the connector is source controlled
# - refactor so that the source and destination catalogs are merged into a single dataframe early on
# - refactor so we are importing a common dataclass
# - check which specs are available
# lets make sure markdown is still working
# then lets get specs all at once
# then lets hoise the merge
# move metadata to its own file

# todo move to lib
def is_spec_cached(dockerRepository, dockerImageTag):
    url = f"https://storage.googleapis.com/io-airbyte-cloud-spec-cache/specs/{dockerRepository}/{dockerImageTag}/spec.json"
    response = requests.head(url)
    return response.status_code == 200

def augment_and_normalize_connector_dataframes(cloud_df, oss_df, primaryKey, connector_type, valid_metadata_list, source_controlled_connectors):
        # Add a column 'is_cloud' to indicate if an image/version pair is in the cloud catalog
    cloud_df["is_cloud"] = True

    # Add a column 'is_oss' to indicate if an image/version pair is in the oss catalog
    oss_df["is_oss"] = True

    composite_key = [primaryKey, "dockerRepository", "dockerImageTag"]

    # Merge the two catalogs on the 'image' and 'version' columns, keeping only the unique pairs
    total_catalog = pd.merge(
        cloud_df, oss_df, how="outer", on=composite_key
    ).drop_duplicates(subset=composite_key)

    merged_catalog = pd.merge(total_catalog, valid_metadata_list[["definitionId", "is_metadata_valid"]], left_on=primaryKey, right_on="definitionId", how="left")

    # Replace NaN values in the 'is_cloud' and 'is_oss' columns with False
    merged_catalog[["is_cloud", "is_oss"]] = merged_catalog[["is_cloud", "is_oss"]].fillna(False)

    # Set connectorType to 'source' or 'destination'
    merged_catalog["connector_type"] = connector_type

    is_source_controlled = lambda x: x.lstrip("airbyte/") in source_controlled_connectors
    merged_catalog['is_source_controlled'] = merged_catalog['dockerRepository'].apply(is_source_controlled)
    merged_catalog['is_spec_cached'] = merged_catalog.apply(lambda x: is_spec_cached(x['dockerRepository'], x['dockerImageTag']), axis=1)

    return merged_catalog

# ASSETS

@asset(required_resource_keys={"catalog_report_directory_manager"}, group_name=GROUP_NAME)
def connector_catalog_location_html(context, all_destinations_dataframe, all_sources_dataframe):
    """
    Generate an HTML report of the connector catalog locations.
    """

    columns_to_show = ["dockerRepository", "dockerImageTag", "is_oss", "is_cloud", "is_source_controlled", "is_spec_cached", "is_metadata_valid"]

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

    columns_to_show = ["dockerRepository", "dockerImageTag", "is_oss", "is_cloud", "is_source_controlled", "is_spec_cached", "is_metadata_valid"]

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
def all_destinations_dataframe(cloud_destinations_dataframe, oss_destinations_dataframe, source_controlled_connectors, valid_metadata_list) -> pd.DataFrame:
    """
    Merge the cloud and oss destinations catalogs into a single dataframe.
    """

    return augment_and_normalize_connector_dataframes(
        cloud_df=cloud_destinations_dataframe,
        oss_df=oss_destinations_dataframe,
        primaryKey="destinationDefinitionId",
        connector_type="destination",
        valid_metadata_list=valid_metadata_list,
        source_controlled_connectors=source_controlled_connectors
    )


@asset(group_name=GROUP_NAME)
def all_sources_dataframe(cloud_sources_dataframe, oss_sources_dataframe, source_controlled_connectors, valid_metadata_list) -> pd.DataFrame:
    """
    Merge the cloud and oss source catalogs into a single dataframe.
    """
    return augment_and_normalize_connector_dataframes(
        cloud_df=cloud_sources_dataframe,
        oss_df=oss_sources_dataframe,
        primaryKey="sourceDefinitionId",
        connector_type="source",
        valid_metadata_list=valid_metadata_list,
        source_controlled_connectors=source_controlled_connectors
    )


@asset(group_name=GROUP_NAME)
def cloud_sources_dataframe(latest_cloud_catalog_dict: dict):
    sources = latest_cloud_catalog_dict["sources"]
    return OutputDataFrame(pd.DataFrame(sources))


@asset(group_name=GROUP_NAME)
def oss_sources_dataframe(latest_oss_catalog_dict: dict):
    sources = latest_oss_catalog_dict["sources"]
    return OutputDataFrame(pd.DataFrame(sources))


@asset(group_name=GROUP_NAME)
def cloud_destinations_dataframe(latest_cloud_catalog_dict: dict):
    destinations = latest_cloud_catalog_dict["destinations"]
    return OutputDataFrame(pd.DataFrame(destinations))


@asset(group_name=GROUP_NAME)
def oss_destinations_dataframe(latest_oss_catalog_dict: dict):
    destinations = latest_oss_catalog_dict["destinations"]
    return OutputDataFrame(pd.DataFrame(destinations))


@asset(required_resource_keys={"latest_cloud_catalog_gcs_file"}, group_name=GROUP_NAME)
def latest_cloud_catalog_dict(context: OpExecutionContext) -> dict:
    oss_catalog_file = context.resources.latest_cloud_catalog_gcs_file
    json_string = oss_catalog_file.download_as_string().decode("utf-8")
    oss_catalog_dict = json.loads(json_string)
    return oss_catalog_dict


@asset(required_resource_keys={"latest_oss_catalog_gcs_file"}, group_name=GROUP_NAME)
def latest_oss_catalog_dict(context: OpExecutionContext) -> dict:
    oss_catalog_file = context.resources.latest_oss_catalog_gcs_file
    json_string = oss_catalog_file.download_as_string().decode("utf-8")
    oss_catalog_dict = json.loads(json_string)
    return oss_catalog_dict
