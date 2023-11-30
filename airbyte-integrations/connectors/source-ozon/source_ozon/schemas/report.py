from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel


class ReportRequest(BaseModel):
    campaigns: list[str]
    dateFrom: Optional[str]
    dateTo: Optional[str]
    groupBy: Optional[Literal["NO_GROUP_BY", "DATE", "START_OF_WEEK", "START_OF_MONTH"]]


class ReportStatusResponse(BaseModel):
    UUID: str
    state: Literal["NOT_STARTED", "IN_PROGRESS", "ERROR", "OK"]
    createdAt: datetime
    updatedAt: datetime
    request: ReportRequest
    error: Optional[str]
    link: Optional[str]
    kind: Literal["STATS", "SEARCH_PHRASES", "ATTRIBUTION", "VIDEO"]
