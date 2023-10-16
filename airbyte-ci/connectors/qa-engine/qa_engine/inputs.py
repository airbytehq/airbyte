#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from enum import Enum
from importlib.resources import files
from typing import Optional

import pandas as pd
import requests

from .constants import CONNECTOR_TEST_SUMMARY_URL

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


def get_connector_build_output_url(connector_technical_name: str) -> str:
    """
    Get the connector build output url.
    """
    # remove connectors/ prefix from connector_technical_name
    connector_technical_name = connector_technical_name.replace("connectors/", "")
    return f"{CONNECTOR_TEST_SUMMARY_URL}/{connector_technical_name}/index.json"


def fetch_latest_build_status_for_connector(connector_technical_name: str) -> BUILD_STATUSES:
    """Fetch the latest build status for a given connector version."""
    connector_build_output_url = get_connector_build_output_url(connector_technical_name)
    connector_build_output_response = requests.get(connector_build_output_url)

    # if the connector returned successfully, return the outcome
    if connector_build_output_response.status_code == 200:
        connector_build_output = connector_build_output_response.json()

        # we want to get the latest build status
        # sort by date and get the first element
        latest_connector_run = sorted(connector_build_output, key=lambda x: x["date"], reverse=True)[0]

        outcome = latest_connector_run.get("success")
        if outcome is None:
            LOGGER.error(f"Error: No outcome value for connector {connector_technical_name}")
            return BUILD_STATUSES.NOT_FOUND

        if outcome == True:
            return BUILD_STATUSES.SUCCESS

        if outcome == False:
            return BUILD_STATUSES.FAILURE

        try:
            return BUILD_STATUSES.from_string(outcome)
        except KeyError:
            LOGGER.error(f"Error: Unexpected build status value: {outcome} for connector {connector_technical_name}")
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
    connector_adoption_sql = files("qa_engine").joinpath("connector_adoption.sql").read_text()
    adoption_metrics = pd.read_gbq(connector_adoption_sql, project_id="airbyte-data-prod")
    return adoption_metrics[
        [
            "connector_definition_id",
            "connector_version",
            "number_of_connections",
            "number_of_users",
            "succeeded_syncs_count",
            "failed_syncs_count",
            "total_syncs_count",
            "sync_success_rate",
        ]
    ]
