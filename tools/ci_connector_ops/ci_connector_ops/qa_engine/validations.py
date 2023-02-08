#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from typing import Iterable

import pandas as pd
import requests

from .constants import INAPPROPRIATE_FOR_CLOUD_USE_CONNECTORS
from .models import ConnectorQAReport, QAReport
from .inputs import fetch_latest_build_status_for_connector_version, BUILD_STATUSES

TRUTHY_COLUMNS_TO_BE_ELIGIBLE = [
  "documentation_is_available",
  "is_appropriate_for_cloud_use",
  "latest_build_is_successful"
]

class QAReportGenerationError(Exception):
    pass

def url_is_reachable(url: str) -> bool:
    response = requests.get(url)
    return response.status_code == 200

def is_appropriate_for_cloud_use(definition_id: str) -> bool:
    return definition_id not in INAPPROPRIATE_FOR_CLOUD_USE_CONNECTORS

def is_eligible_for_promotion_to_cloud(connector_qa_data: pd.Series) -> bool:
  if connector_qa_data["is_on_cloud"]:
    return False
  return all([
    connector_qa_data[col]
    for col in TRUTHY_COLUMNS_TO_BE_ELIGIBLE
  ])

def latest_build_is_successful(connector_qa_data: pd.Series) -> bool:
    connector_technical_name = connector_qa_data["connector_technical_name"]
    connector_version = connector_qa_data["connector_version"]
    latest_build_status = fetch_latest_build_status_for_connector_version(connector_technical_name, connector_version)
    return latest_build_status == BUILD_STATUSES.SUCCESS

def get_qa_report(enriched_catalog: pd.DataFrame, oss_catalog_length: int) -> pd.DataFrame:
    """Perform validation steps on top of the enriched catalog.
    Adds the following columns:
      - documentation_is_available:
        GET the documentation URL and expect a 200 status code.
      - is_appropriate_for_cloud_use:
        Determined from an hardcoded list of definition ids inappropriate for cloud use.
      - latest_build_is_successful:
        Check if the latest build for the current connector version is successful.
      - number_of_connections:
        Get the number of connections using this connector version from our datawarehouse.
      - number_of_users:
        Get the number of users using this connector version from our datawarehouse.
      - sync_success_rate:
        Get the sync success rate of the connections with this connector version from our datawarehouse.
    Args:
        enriched_catalog (pd.DataFrame): The enriched catalog.
        oss_catalog_length (pd.DataFrame): The length of the OSS catalog, for sanity check.

    Returns:
        pd.DataFrame: The final QA report.
    """
    qa_report = enriched_catalog.copy(deep=True)
    qa_report["documentation_is_available"] = qa_report.documentation_url.apply(url_is_reachable)
    qa_report["is_appropriate_for_cloud_use"] = qa_report.connector_definition_id.apply(is_appropriate_for_cloud_use)

    qa_report["latest_build_is_successful"] = qa_report.apply(latest_build_is_successful, axis="columns")

    qa_report["is_eligible_for_promotion_to_cloud"] = qa_report.apply(is_eligible_for_promotion_to_cloud, axis="columns")
    qa_report["report_generation_datetime"] = datetime.utcnow()

    # Only select dataframe columns defined in the ConnectorQAReport model.
    qa_report= qa_report[[field.name for field in ConnectorQAReport.__fields__.values()]]
    # Validate the report structure with pydantic QAReport model.
    QAReport(connectors_qa_report=qa_report.to_dict(orient="records"))
    if len(qa_report) != oss_catalog_length:
      raise QAReportGenerationError("The QA report does not contain all the connectors defined in the OSS catalog.")
    return qa_report

def get_connectors_eligible_for_cloud(qa_report: pd.DataFrame) -> Iterable[ConnectorQAReport]:
    for _, row in qa_report[qa_report["is_eligible_for_promotion_to_cloud"]].iterrows():
      yield ConnectorQAReport(**row)
