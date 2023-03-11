import pandas as pd
import json

from dagster import MetadataValue, Output, asset, OpExecutionContext

from ..utils.html import html_body

# ------ Assets ------ #

@asset(required_resource_keys={"catalog_report_directory_manager"})
def connector_catalog_location_html(context, all_destinations_dataframe, all_sources_dataframe):
    columns_to_show = ['name_x', 'dockerRepository', 'dockerImageTag', 'is_oss', 'is_cloud']

    # convert true and false to checkmarks and x's
    all_sources_dataframe.replace({True: '✅', False: '❌'}, inplace=True)
    all_destinations_dataframe.replace({True: '✅', False: '❌'}, inplace=True)

    title = "Connector Catalogs"
    content = f"<h1>{title}</h1>"
    content += f"<h2>Sources</h2>"
    content += all_sources_dataframe[columns_to_show].to_html()
    content += f"<h2>Destinations</h2>"
    content += all_destinations_dataframe[columns_to_show].to_html()

    html = html_body(title, content)

    catalog_report_directory_manager = context.resources.catalog_report_directory_manager
    file_handle = catalog_report_directory_manager.write_data(html.encode(), ext="html", key="connector_catalog_locations")

    metadata = {
        "gcs_path": MetadataValue.url(file_handle.gcs_path),
    }

    return Output(metadata=metadata, value=file_handle)

@asset(required_resource_keys={"catalog_report_directory_manager"})
def connector_catalog_location_markdown(context, all_destinations_dataframe, all_sources_dataframe):
    columns_to_show = ['name_x', 'dockerRepository', 'dockerImageTag', 'is_oss', 'is_cloud']

    # convert true and false to checkmarks and x's
    all_sources_dataframe.replace({True: '✅', False: '❌'}, inplace=True)
    all_destinations_dataframe.replace({True: '✅', False: '❌'}, inplace=True)

    markdown = f"# Connector Catalog Locations\n\n"
    markdown += f"## Sources\n"
    markdown += all_sources_dataframe[columns_to_show].to_markdown()
    markdown += f"\n\n## Destinations\n"
    markdown += all_destinations_dataframe[columns_to_show].to_markdown()

    catalog_report_directory_manager = context.resources.catalog_report_directory_manager
    file_handle = catalog_report_directory_manager.write_data(markdown.encode(), ext="md", key="connector_catalog_locations")

    metadata = {
        "preview": MetadataValue.md(markdown),
        "gcs_path": MetadataValue.url(file_handle.gcs_path),
    }
    return Output(metadata=metadata, value=file_handle)

@asset
def all_destinations_dataframe(cloud_destinations_dataframe, oss_destinations_dataframe):
    # Add a column 'is_cloud' to indicate if an image/version pair is in the cloud catalog
    cloud_destinations_dataframe['is_cloud'] = True

    # Add a column 'is_oss' to indicate if an image/version pair is in the oss catalog
    oss_destinations_dataframe['is_oss'] = True

    composite_key = ['dockerRepository', 'dockerImageTag']

    # Merge the two catalogs on the 'image' and 'version' columns, keeping only the unique pairs
    merged_catalog = pd.merge(cloud_destinations_dataframe, oss_destinations_dataframe, how='outer', on=composite_key).drop_duplicates(subset=composite_key)

    # Replace NaN values in the 'is_cloud' and 'is_oss' columns with False
    merged_catalog[['is_cloud', 'is_oss']] = merged_catalog[['is_cloud', 'is_oss']].fillna(False)

    # Return the merged catalog with the desired columns
    return merged_catalog


@asset
def all_sources_dataframe(cloud_sources_dataframe, oss_sources_dataframe):
    # Add a column 'is_cloud' to indicate if an image/version pair is in the cloud catalog
    cloud_sources_dataframe['is_cloud'] = True

    # Add a column 'is_oss' to indicate if an image/version pair is in the oss catalog
    oss_sources_dataframe['is_oss'] = True

    composite_key = ['dockerRepository', 'dockerImageTag']

    # Merge the two catalogs on the 'image' and 'version' columns, keeping only the unique pairs
    merged_catalog = pd.merge(cloud_sources_dataframe, oss_sources_dataframe, how='outer', on=composite_key).drop_duplicates(subset=composite_key)

    # Replace NaN values in the 'is_cloud' and 'is_oss' columns with False
    merged_catalog[['is_cloud', 'is_oss']] = merged_catalog[['is_cloud', 'is_oss']].fillna(False)

    # Return the merged catalog with the desired columns
    return merged_catalog

@asset
def cloud_sources_dataframe(latest_cloud_catalog_dict):
    sources = latest_cloud_catalog_dict["sources"]
    return pd.DataFrame(sources)

@asset
def oss_sources_dataframe(latest_oss_catalog_dict):
    sources = latest_oss_catalog_dict["sources"]
    return pd.DataFrame(sources)

@asset
def cloud_destinations_dataframe(latest_cloud_catalog_dict):
    destinations = latest_cloud_catalog_dict["destinations"]
    return pd.DataFrame(destinations)

@asset
def oss_destinations_dataframe(latest_oss_catalog_dict):
    destinations = latest_oss_catalog_dict["destinations"]
    return pd.DataFrame(destinations)

@asset(required_resource_keys={"latest_cloud_catalog_gcs_file"})
def latest_cloud_catalog_dict(context: OpExecutionContext):
    oss_catalog_file = context.resources.latest_cloud_catalog_gcs_file
    json_string = oss_catalog_file.download_as_string().decode('utf-8')
    oss_catalog_dict = json.loads(json_string)
    return oss_catalog_dict

# TODO add partitions
@asset(required_resource_keys={"latest_oss_catalog_gcs_file"})
def latest_oss_catalog_dict(context: OpExecutionContext):
    oss_catalog_file = context.resources.latest_oss_catalog_gcs_file
    json_string = oss_catalog_file.download_as_string().decode('utf-8')
    oss_catalog_dict = json.loads(json_string)
    return oss_catalog_dict
