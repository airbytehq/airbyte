import pandas as pd

from dagster import MetadataValue, Output, asset

from metadata_service.models.generated.ConnectorMetadataDefinitionV0 import ConnectorMetadataDefinitionV0

GROUP_NAME = "metadata"


# HELPERS

OSS_SUFFIX = "_oss"
CLOUD_SUFFIX = "_cloud"


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

    allowed_overrides = [
        "name",
        "dockerRepository",
        "dockerImageTag",
        "supportsDbt",
        "supportsNormalization",
        "license",
        "supportUrl",
        "sourceType",
        "allowedHosts",
        "normalizationConfig",
        "suggestedStreams",
        "resourceRequirements",
    ]

    # check if the columns are the same
    # TODO refactor this to handle cloud only
    for override_col in allowed_overrides:
        oss_col = override_col + OSS_SUFFIX
        cloud_col = override_col + CLOUD_SUFFIX

        cloud_value = merged_df.get(cloud_col)
        oss_value = merged_df.get(oss_col)

        # if the columns are different, add the cloud value to the overrides
        # TODO do a deep comparison
        if cloud_value and oss_value != cloud_value:
            catalogs["cloud"][override_col] = merged_df.get(cloud_col)

    return catalogs;

def merge_into_metadata_definitions(id_field, connector_type, oss_connector_df, cloud_connector_df) -> pd.Series:
    merged_connectors = pd.merge(oss_connector_df, cloud_connector_df, on=id_field, how='outer', suffixes=(OSS_SUFFIX, CLOUD_SUFFIX), indicator=True)
    sanitized_connectors = merged_connectors.where(pd.notnull(merged_connectors), None)
    def build_metadata(merged_df):
        raw_data = {
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

            "supportsDbt": get_field_with_fallback(merged_df, "supportsDbt"),
            "supportsNormalization": get_field_with_fallback(merged_df, "supportsNormalization"),
            "allowedHosts": get_field_with_fallback(merged_df, "allowedHosts"),
            "normalizationConfig": get_field_with_fallback(merged_df, "normalizationConfig"),
            "suggestedStreams": get_field_with_fallback(merged_df, "suggestedStreams"),
            "resourceRequirements": get_field_with_fallback(merged_df, "resourceRequirements"),
        }

        # remove none values
        data = {k: v for k, v in raw_data.items() if v is not None}

        metadata = {
            "metadataSpecVersion": "1.0",
            "data": data
        }

        catalogs = compute_catalog_overrides(merged_df)
        metadata["data"]["catalogs"] = catalogs

        return metadata

    metadata_list = [build_metadata(merged_df) for _, merged_df in sanitized_connectors.iterrows()]

    return metadata_list

def validate_metadata(metadata):
    try:
        ConnectorMetadataDefinitionV0.parse_obj(metadata)
        return True, None
    except Exception as e:
        return False, str(e)

# ASSETS


@asset(group_name=GROUP_NAME)
def valid_metadata_list(catalog_derived_metadata_definitions):
    result = []

    for metadata in catalog_derived_metadata_definitions:
        valid, error_msg = validate_metadata(metadata)
        result.append({
            'definitionId': metadata["data"]['definitionId'],
            'name': metadata["data"]['name'],
            'dockerRepository': metadata["data"]['dockerRepository'],
            'is_metadata_valid': valid,
            'error_msg': error_msg
        })

    result_df = pd.DataFrame(result)

    return Output(result_df, metadata={"count": len(result_df), "preview": MetadataValue.md(result_df.to_markdown())})


@asset(group_name=GROUP_NAME)
def catalog_derived_metadata_definitions(context, cloud_sources_dataframe, cloud_destinations_dataframe, oss_sources_dataframe, oss_destinations_dataframe):
    sources_metadata_list = merge_into_metadata_definitions("sourceDefinitionId", "source", oss_sources_dataframe, cloud_sources_dataframe)
    destinations_metadata_list = merge_into_metadata_definitions("destinationDefinitionId", "destination", oss_destinations_dataframe, cloud_destinations_dataframe)
    all_definitions = sources_metadata_list + destinations_metadata_list;
    context.log.info(f"Found {len(all_definitions)} metadata definitions")
    return Output(all_definitions, metadata={"count": len(all_definitions)})
