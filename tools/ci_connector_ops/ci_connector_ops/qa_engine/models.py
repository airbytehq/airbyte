#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, Field

class ConnectorTypeEnum(str, Enum):
    source = "source"
    destination = "destination"

class ReleaseStageEnum(str, Enum):
    unknown = "unknown"
    alpha = "alpha"
    beta = "beta"
    generally_available = "generally_available"

PUBLIC_FIELD = Field(..., is_public=True)
PRIVATE_FIELD = Field(..., is_public=False)

class ConnectorQAReport(BaseModel):
    connector_type: ConnectorTypeEnum = PUBLIC_FIELD
    connector_name: str = PUBLIC_FIELD
    connector_technical_name: str = PUBLIC_FIELD
    connector_definition_id: str = PUBLIC_FIELD
    connector_version: str = PUBLIC_FIELD
    release_stage: ReleaseStageEnum = PUBLIC_FIELD
    is_on_cloud: bool = PUBLIC_FIELD
    is_appropriate_for_cloud_use: bool = PUBLIC_FIELD
    latest_build_is_successful: bool = PUBLIC_FIELD
    documentation_is_available: bool = PUBLIC_FIELD
    number_of_connections: int = PRIVATE_FIELD
    number_of_users: int = PRIVATE_FIELD
    sync_success_rate: float = PRIVATE_FIELD
    total_syncs_count: int = PRIVATE_FIELD
    failed_syncs_count: int = PRIVATE_FIELD
    succeeded_syncs_count: int = PRIVATE_FIELD
    is_eligible_for_promotion_to_cloud: bool = PUBLIC_FIELD
    report_generation_datetime: datetime = PUBLIC_FIELD

class QAReport(BaseModel):
    connectors_qa_report: List[ConnectorQAReport]
