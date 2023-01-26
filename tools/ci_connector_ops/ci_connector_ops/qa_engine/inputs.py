#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os
from importlib.resources import files
import json

from google.oauth2 import service_account
import requests
import pandas as pd

from .constants import CLOUD_CATALOG_URL, OSS_CATALOG_URL

def fetch_remote_catalog(catalog_url: str) -> pd.DataFrame:
    """Fetch a combined remote catalog and return a single DataFrame 
    with sources and destinations defined by the connector_type column.

    Args:
        catalog_url (str): The remote catalog url.

    Returns:
        pd.DataFrame: Sources and destinations combined under a denormalized DataFrame.
    """
    raw_catalog = requests.get(catalog_url).json()
    sources = pd.DataFrame(raw_catalog["sources"])
    destinations = pd.DataFrame(raw_catalog["destinations"])
    sources["connector_type"] = "source"
    sources["connector_definition_id"] = sources.sourceDefinitionId
    destinations["connector_type"] = "destination"
    destinations["connector_definition_id"] = destinations.destinationDefinitionId
    return pd.concat([sources, destinations])

def fetch_adoption_metrics_per_connector_version() -> pd.DataFrame:
    """Retrieve adoptions metrics for each connector version from our data warehouse.

    Returns:
        pd.DataFrame: A dataframe with adoption metrics per connector version.
    """
    connector_adoption_sql = files("ci_connector_ops.qa_engine").joinpath("connector_adoption.sql").read_text()
    bq_credentials = service_account.Credentials.from_service_account_info(json.loads(os.environ["QA_ENGINE_AIRBYTE_DATA_PROD_SA"]))
    adoption_metrics = pd.read_gbq(connector_adoption_sql, project_id="airbyte-data-prod", credentials=bq_credentials)
    return adoption_metrics[[
        "connector_definition_id",
        "connector_version",
        "number_of_connections",
        "number_of_users",
        "succeeded_syncs_count",
        "failed_syncs_count",
        "total_syncs_count",
        "sync_success_rate",
    ]]

CLOUD_CATALOG = fetch_remote_catalog(CLOUD_CATALOG_URL)
OSS_CATALOG = fetch_remote_catalog(OSS_CATALOG_URL)
