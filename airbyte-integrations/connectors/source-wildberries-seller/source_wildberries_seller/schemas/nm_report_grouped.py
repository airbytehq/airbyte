from typing import Optional, List

from pydantic import BaseModel, Field

from source_wildberries_seller.schemas.common import (
    NmReportTag,
    NmReportObject,
    NmReportStatistics,
    NmReportResponseAdditionalError,
)


class GroupedNmReport(BaseModel):
    brandName: Optional[str] = Field(description="Название бренда")
    tags: List[NmReportTag] = Field(description="Теги", default=[])
    object: Optional[NmReportObject] = Field(description="Предмет")
    statistics: Optional[NmReportStatistics] = Field(description="Статистика")


class GroupedNmReportResponseData(BaseModel):
    page: int
    isNextPage: bool
    groups: List[GroupedNmReport] = []


class GroupedNmReportResponse(BaseModel):
    data: GroupedNmReportResponseData
    error: bool
    errorText: Optional[str]
    additionalErrors: Optional[List[NmReportResponseAdditionalError]]
