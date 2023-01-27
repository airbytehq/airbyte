#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pandas as pd
import requests

from .constants import INAPPROPRIATE_FOR_CLOUD_USE_CONNECTORS
from .inputs import OSS_CATALOG
from .models import ConnectorQAReport, QAReport

class QAReportGenerationError(Exception):
    pass

def url_is_reachable(url: str) -> bool:
    response = requests.get(url)
    return response.status_code == 200

def is_appropriate_for_cloud_use(definition_id: str) -> bool:
    return definition_id not in INAPPROPRIATE_FOR_CLOUD_USE_CONNECTORS

def get_qa_report(enriched_catalog: pd.DataFrame) -> pd.DataFrame:
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

    Returns:
        pd.DataFrame: The final QA report.
    """
    qa_report = enriched_catalog.copy(deep=True)
    qa_report["documentation_is_available"] = qa_report.documentation_url.apply(url_is_reachable)
    qa_report["is_appropriate_for_cloud_use"] = qa_report.connector_definition_id.apply(is_appropriate_for_cloud_use)
    
    # TODO YET TO IMPLEMENT VALIDATIONS
    qa_report["latest_build_is_successful"] = False # TODO, tracked in https://github.com/airbytehq/airbyte/issues/21720
    qa_report["number_of_connections"] = 0 # TODO, tracked in https://github.com/airbytehq/airbyte/issues/21721
    qa_report["number_of_users"] = 0 # TODO, tracked in https://github.com/airbytehq/airbyte/issues/21721
    qa_report["sync_success_rate"] = .0 # TODO, tracked in https://github.com/airbytehq/airbyte/issues/21721

    # Only select dataframe columns defined in the ConnectorQAReport model.
    qa_report= qa_report[[field.name for field in ConnectorQAReport.__fields__.values()]]
    # Validate the report structure with pydantic QAReport model.
    QAReport(connectors_qa_report=qa_report.to_dict(orient="records"))
    if len(qa_report) != len(OSS_CATALOG):
        raise QAReportGenerationError("The QA report does not contain all the connectors defined in the OSS catalog.")
    return qa_report
