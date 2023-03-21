import pandas as pd
import json
import requests
import pandas as pd
from metadata_service.models.generated.ConnectorMetadataDefinitionV0 import ConnectorMetadataDefinitionV0

from dagster import MetadataValue, Output, asset, OpExecutionContext
from jinja2 import Environment, PackageLoader

def render_connector_catalog_locations_html(destinations_table, sources_table):
    env = Environment(loader=PackageLoader("orchestrator", "templates"))
    template = env.get_template("connector_catalog_locations.html")
    return template.render(destinations_table=destinations_table, sources_table=sources_table)

def render_connector_catalog_locations_markdown(destinations_markdown, sources_markdown):
    env = Environment(loader=PackageLoader("orchestrator", "templates"))
    template = env.get_template("connector_catalog_locations.md")
    return template.render(destinations_markdown=destinations_markdown, sources_markdown=sources_markdown)


OSS_SUFFIX = "_oss"
CLOUD_SUFFIX = "_cloud"

def load_json_from_file(path):
    with open(path) as f:
        return json.load(f)

def get_primary_catalog_suffix(merged_df):
    cloud_only = merged_df["_merge"] == "right_only"
    primary_suffix = CLOUD_SUFFIX if cloud_only else OSS_SUFFIX
    secondary_suffix = OSS_SUFFIX if cloud_only else CLOUD_SUFFIX
    return primary_suffix, secondary_suffix

def get_field_with_fallback(merged_df, field):
    primary_suffix, secondary_suffix = get_primary_catalog_suffix(merged_df)

    primary_field = field + primary_suffix
    secondary_field = field + secondary_suffix

    secondary_value = merged_df.get(secondary_field)
    return merged_df.get(primary_field, default=secondary_value)

def compute_catalog_overrides(merged_df):
    cloud_only = merged_df["_merge"] == "right_only";
    oss_only = merged_df["_merge"] == "left_only";

    catalogs = {
        "oss": {
            "enabled": not cloud_only,
        },
        "cloud": {
            "enabled": not oss_only,
        }
    }

    # find the difference between the two catalogs
    if cloud_only or oss_only:
        return catalogs

    # get all columns ending with _oss
    all_oss_columns = [col for col in merged_df.index if col.endswith(OSS_SUFFIX)]


    # check if the columns are the same
    # TODO refactor this to handle cloud only
    for oss_col in all_oss_columns:
        equivalent_cloud_col = oss_col.replace(OSS_SUFFIX, CLOUD_SUFFIX)
        if merged_df.get(oss_col) != merged_df.get(equivalent_cloud_col):
            col_name = oss_col.replace(OSS_SUFFIX, "")
            catalogs["cloud"][col_name] = merged_df.get(equivalent_cloud_col)

    return catalogs;


def merge_into_metadata_definitions(id_field, connector_type, oss_connector_df, cloud_connector_df) -> pd.Series:
    merged_connectors = pd.merge(oss_connector_df, cloud_connector_df, on=id_field, how='outer', suffixes=(OSS_SUFFIX, CLOUD_SUFFIX), indicator=True)

    def build_metadata(merged_df):
        metadata = {
            "metadataSpecVersion": "1.0",
            "data": {
                "name": get_field_with_fallback(merged_df, "name"),
                "definitionId": merged_df[id_field],
                "connectorType": connector_type,
                "dockerRepository": get_field_with_fallback(merged_df, "dockerRepository"),
                "githubIssueLabel": get_field_with_fallback(merged_df, "dockerRepository").replace("airbyte/", ""),
                "dockerImageTag": get_field_with_fallback(merged_df, "dockerImageTag"),
                "icon": get_field_with_fallback(merged_df, "icon"),
                "supportUrl": get_field_with_fallback(merged_df, "documentationUrl"),
                "sourceType": get_field_with_fallback(merged_df, "sourceType"),
                "releaseStage": get_field_with_fallback(merged_df, "releaseStage"),
                "license": "MIT",
            }
        }

        catalogs = compute_catalog_overrides(merged_df)
        metadata["data"]["catalogs"] = catalogs

        return pd.DataFrame(metadata)

    metadata_list = merged_connectors.apply(build_metadata, axis=1)

    return metadata_list

def validate_metadata(metadata):
    try:
        ConnectorMetadataDefinitionV0.parse_obj(metadata)
        return True, None
    except Exception as e:
        print(e)
        return False, str(e)

@asset
def valid_metadata_list(metadata_definitions) -> pd.DataFrame:
    result = []

    for metadata in metadata_definitions:
        valid, error_msg = validate_metadata(metadata)
        result.append({
            'definitionId': metadata["data"]['definitionId'],
            'name': metadata["data"]['name'],
            'dockerRepository': metadata["data"]['dockerRepository'],
            'is_metadata_valid': valid,
            'error_msg': error_msg
        })

    result_df = pd.DataFrame(result)

    return result_df
    # return Output(result_df, metadata={"count": len(result_df), "preview": MetadataValue.md(result_df.to_markdown())})

@asset
def metadata_definitions(cloud_sources_dataframe, cloud_destinations_dataframe, oss_sources_dataframe, oss_destinations_dataframe) -> pd.Series:
    sources_metadata_list = merge_into_metadata_definitions("sourceDefinitionId", "source", oss_sources_dataframe, cloud_sources_dataframe)
    destinations_metadata_list = merge_into_metadata_definitions("destinationDefinitionId", "destination", oss_destinations_dataframe, cloud_destinations_dataframe)
    all_definitions = pd.concat([sources_metadata_list, destinations_metadata_list]);
    return all_definitions;
    # return Output(all_definitions, metadata={"count": len(all_definitions), "preview_of_one": MetadataValue.md(all_definitions[0]["data"].to_markdown())})


@asset(required_resource_keys={"catalog_report_directory_manager"})
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


@asset(required_resource_keys={"catalog_report_directory_manager"})
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

# TODO
# - add  column for whether the connector is source controlled
# - refactor so that the source and destination catalogs are merged into a single dataframe early on
# - refactor so we are importing a common dataclass
# - check which specs are available

def is_spec_cached(dockerRepository, dockerImageTag):
    url = f"https://storage.googleapis.com/io-airbyte-cloud-spec-cache/specs/{dockerRepository}/{dockerImageTag}/spec.json"
    response = requests.head(url)
    return response.status_code == 200

@asset
def all_destinations_dataframe(cloud_destinations_dataframe, oss_destinations_dataframe, source_controlled_connectors, valid_metadata_list) -> pd.DataFrame:
    """
    Merge the cloud and oss destinations catalogs into a single dataframe.
    """

    # Add a column 'is_cloud' to indicate if an image/version pair is in the cloud catalog
    cloud_destinations_dataframe["is_cloud"] = True

    # Add a column 'is_oss' to indicate if an image/version pair is in the oss catalog
    oss_destinations_dataframe["is_oss"] = True

    composite_key = ["destinationDefinitionId", "dockerRepository", "dockerImageTag"]

    # Merge the two catalogs on the 'image' and 'version' columns, keeping only the unique pairs
    merged_catalog = pd.merge(
        cloud_destinations_dataframe, oss_destinations_dataframe, how="outer", on=composite_key
    ).drop_duplicates(subset=composite_key)

    # Replace NaN values in the 'is_cloud' and 'is_oss' columns with False
    merged_catalog[["is_cloud", "is_oss"]] = merged_catalog[["is_cloud", "is_oss"]].fillna(False)

    is_source_controlled = lambda x: x.lstrip("airbyte/") in source_controlled_connectors
    merged_catalog['is_source_controlled'] = merged_catalog['dockerRepository'].apply(is_source_controlled)
    merged_catalog['is_spec_cached'] = merged_catalog.apply(lambda x: is_spec_cached(x['dockerRepository'], x['dockerImageTag']), axis=1)
    merged_catalog['is_metadata_valid'] = merged_catalog["destinationDefinitionId"].apply(lambda x: x in valid_metadata_list.loc[x]["is_metadata_valid"])

    # Return the merged catalog with the desired columns
    return merged_catalog


@asset
def all_sources_dataframe(cloud_sources_dataframe, oss_sources_dataframe, source_controlled_connectors, valid_metadata_list) -> pd.DataFrame:
    """
    Merge the cloud and oss source catalogs into a single dataframe.
    """

    # Add a column 'is_cloud' to indicate if an image/version pair is in the cloud catalog
    cloud_sources_dataframe["is_cloud"] = True

    # Add a column 'is_oss' to indicate if an image/version pair is in the oss catalog
    oss_sources_dataframe["is_oss"] = True

    composite_key = ["sourceDefinitionId", "dockerRepository", "dockerImageTag"]

    # Merge the two catalogs on the 'image' and 'version' columns, keeping only the unique pairs
    total_catalog = pd.merge(
        cloud_sources_dataframe, oss_sources_dataframe, how="outer", on=composite_key
    ).drop_duplicates(subset=composite_key)

    # import pdb; pdb.set_trace()
    merged_catalog = pd.merge(total_catalog, valid_metadata_list[["definitionId", "is_metadata_valid"]], left_on="sourceDefinitionId", right_on="definitionId", how="left")

    # Replace NaN values in the 'is_cloud' and 'is_oss' columns with False
    merged_catalog[["is_cloud", "is_oss"]] = merged_catalog[["is_cloud", "is_oss"]].fillna(False)

    is_source_controlled = lambda x: x.lstrip("airbyte/") in source_controlled_connectors
    merged_catalog['is_source_controlled'] = merged_catalog['dockerRepository'].apply(is_source_controlled)
    # merged_catalog['is_spec_cached'] = merged_catalog.apply(lambda x: is_spec_cached(x['dockerRepository'], x['dockerImageTag']), axis=1)
    # pdb.set_trace()
    # Return the merged catalog with the desired columns
    return merged_catalog


@asset
def cloud_sources_dataframe(latest_cloud_catalog_dict: dict) -> pd.DataFrame:
    sources = latest_cloud_catalog_dict["sources"]
    return pd.DataFrame(sources)


@asset
def oss_sources_dataframe(latest_oss_catalog_dict: dict) -> pd.DataFrame:
    sources = latest_oss_catalog_dict["sources"]
    return pd.DataFrame(sources)


@asset
def cloud_destinations_dataframe(latest_cloud_catalog_dict: dict) -> pd.DataFrame:
    destinations = latest_cloud_catalog_dict["destinations"]
    return pd.DataFrame(destinations)


@asset
def oss_destinations_dataframe(latest_oss_catalog_dict: dict) -> pd.DataFrame:
    destinations = latest_oss_catalog_dict["destinations"]
    return pd.DataFrame(destinations)


@asset(required_resource_keys={"latest_cloud_catalog_gcs_file"})
def latest_cloud_catalog_dict(context: OpExecutionContext) -> dict:
    oss_catalog_file = context.resources.latest_cloud_catalog_gcs_file
    json_string = oss_catalog_file.download_as_string().decode("utf-8")
    oss_catalog_dict = json.loads(json_string)
    return oss_catalog_dict


@asset(required_resource_keys={"latest_oss_catalog_gcs_file"})
def latest_oss_catalog_dict(context: OpExecutionContext) -> dict:
    oss_catalog_file = context.resources.latest_oss_catalog_gcs_file
    json_string = oss_catalog_file.download_as_string().decode("utf-8")
    oss_catalog_dict = json.loads(json_string)
    return oss_catalog_dict
