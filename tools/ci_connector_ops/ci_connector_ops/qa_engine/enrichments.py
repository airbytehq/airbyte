#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pandas as pd

def get_enriched_catalog(oss_catalog: pd.DataFrame, cloud_catalog: pd.DataFrame) -> pd.DataFrame:
    """Merge OSS and Cloud catalog in a single dataframe on their definition id.
    Transformations:
      - Rename columns to snake case.
      - Rename name column to connector_name.
      - Rename docker_image_tag to connector_version.
      - Replace null value for release_stage with alpha.
    Enrichments:
      - is_on_cloud: determined by the merge operation results.
      - connector_technical_name: built from the docker repository field. airbyte/source-pokeapi -> source-pokeapi.
    Args:
        oss_catalog (pd.DataFrame): The open source catalog dataframe.
        cloud_catalog (pd.DataFrame): The cloud catalog dataframe.

    Returns:
        pd.DataFrame: The enriched catalog.
    """
    enriched_catalog = pd.merge(
        oss_catalog,
        cloud_catalog,
        how="left",
        on="connector_definition_id",
        indicator=True,
        suffixes=("", "_del"),
    )
    enriched_catalog.columns = enriched_catalog.columns.str.replace(
        "(?<=[a-z])(?=[A-Z])", "_", regex=True
    ).str.lower() # column names to snake case
    enriched_catalog["is_on_cloud"] = enriched_catalog["_merge"] == "both"
    enriched_catalog = enriched_catalog.drop(columns="_merge")
    enriched_catalog["connector_name"] = enriched_catalog["name"]
    enriched_catalog["connector_technical_name"] = enriched_catalog["docker_repository"].str.replace("airbyte/", "")
    enriched_catalog["connector_version"] = enriched_catalog["docker_image_tag"]
    enriched_catalog["release_stage"] = enriched_catalog["release_stage"].fillna("unknown")
    return enriched_catalog
