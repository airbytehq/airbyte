from typing import Optional, List

from pydantic import BaseModel, Field

from source_wildberries_seller.schemas.common import (
    NmReportHistory,
    NmReportObject,
    NmReportTag,
    NmReportResponseAdditionalError,
)


class GroupedHistoryNmReport(BaseModel):
    object: Optional[NmReportObject] = Field(description="Предмет")
    brandName: Optional[str] = Field(description="Название бренда")
    tag: Optional[NmReportTag] = Field(description="Тег")
    history: List[NmReportHistory] = []


class GroupedHistoryNmReportResponse(BaseModel):
    data: List[GroupedHistoryNmReport] = []
    error: bool
    errorText: Optional[str]
    additionalErrors: Optional[List[NmReportResponseAdditionalError]]
