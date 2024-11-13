# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from pydantic.v1 import BaseModel


class RecordType(str, Enum):
    CAMPAIGNS = "campaigns"
    ADGROUPS = "adGroups"
    PRODUCTADS = "productAds"
    TARGETS = "targets"
    ASINS = "asins"


class Status(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    COMPLETED = "COMPLETED"
    FAILURE = "FAILURE"


class ReportInitResponse(BaseModel):
    reportId: str
    status: str


class ReportStatus(BaseModel):
    status: str
    location: Optional[str] = None
    url: Optional[str]


@dataclass
class ReportInfo:
    report_id: str
    profile_id: int
    record_type: Optional[str]
    status: Status
    metric_objects: List[dict]
