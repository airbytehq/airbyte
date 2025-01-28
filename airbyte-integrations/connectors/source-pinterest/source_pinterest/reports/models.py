#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from enum import Enum
from typing import List, Optional

from pydantic.v1 import BaseModel


class ReportStatus(str, Enum):
    """Enum Class to define the possible status of a report"""

    DOES_NOT_EXIST = "DOES_NOT_EXIST"
    EXPIRED = "EXPIRED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    FINISHED = "FINISHED"
    IN_PROGRESS = "IN_PROGRESS"


class ReportStatusDetails(BaseModel):
    """Model to capture details of the report status"""

    report_status: ReportStatus
    url: Optional[str]
    size: Optional[int]


class ReportInfo(BaseModel):
    """Model to capture details of the report info"""

    report_status: ReportStatus
    token: str
    message: Optional[str]
    metrics: Optional[List[dict]]
