#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os
from importlib.resources import files
import json
import logging

from .constants import CONNECTOR_BUILD_OUTPUT_URL

from google.oauth2 import service_account
import requests
import pandas as pd
from typing import Optional

from enum import Enum

LOGGER = logging.getLogger(__name__)

class BUILD_STATUSES(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    NOT_FOUND = None

    @classmethod
    def from_string(cls, string_value: Optional[str]) -> "BUILD_STATUSES":
        if string_value is None:
            return BUILD_STATUSES.NOT_FOUND

        return BUILD_STATUSES[string_value.upper()]



def get_connector_build_output_url(connector_technical_name: str, connector_version: str) -> str:
    return f"{CONNECTOR_BUILD_OUTPUT_URL}/{connector_technical_name}/version-{connector_version}.json"

def fetch_latest_build_status_for_connector_version(connector_technical_name: str, connector_version: str) ->BUILD_STATUSES:
    """Fetch the latest build status for a given connector version."""
    connector_build_output_url = get_connector_build_output_url(connector_technical_name, connector_version)
    connector_build_output_response = requests.get(connector_build_output_url)

    # if the connector returned successfully, return the outcome
    if connector_build_output_response.status_code == 200:
        connector_build_output = connector_build_output_response.json()
        outcome = connector_build_output.get("outcome")

        try:
            return BUILD_STATUSES.from_string(outcome)
        except KeyError:
            LOGGER.error(f"Error: Unexpected build status value: {outcome} for connector {connector_technical_name}:{connector_version}")
            return BUILD_STATUSES.NOT_FOUND

    else:
        return BUILD_STATUSES.NOT_FOUND

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
