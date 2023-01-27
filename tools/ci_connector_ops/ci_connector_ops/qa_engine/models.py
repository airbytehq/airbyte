#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel

class ConnectorTypeEnum(str, Enum):
    source = "source"
    destination = "destination"

class ReleaseStageEnum(str, Enum):
    unknown = "unknown"
    alpha = "alpha"
    beta = "beta"
    generally_available = "generally_available"

class ConnectorQAReport(BaseModel):
    connector_type: ConnectorTypeEnum
    connector_name: str
    connector_technical_name: str
    connector_definition_id: str
    connector_version: str
    release_stage: ReleaseStageEnum
    is_on_cloud: bool
    is_appropriate_for_cloud_use: bool
    latest_build_is_successful: bool
    documentation_is_available: bool
    number_of_connections: int 
    number_of_users: int
    sync_success_rate: float
    is_eligible_for_promotion_to_cloud: bool
    report_generation_datetime: datetime

class QAReport(BaseModel):
    connectors_qa_report: List[ConnectorQAReport]
