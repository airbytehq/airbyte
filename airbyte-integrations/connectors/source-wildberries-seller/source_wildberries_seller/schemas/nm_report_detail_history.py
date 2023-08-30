from typing import Optional, List

from pydantic import BaseModel, Field

from source_wildberries_seller.schemas.common import NmReportHistory, NmReportResponseAdditionalError


class DetailHistoryNmReport(BaseModel):
    nmID: Optional[int] = Field(description="Артикул WB")
    imtName: Optional[str] = Field(description="Наименование КТ")
    vendorCode: Optional[str] = Field(description="Артикул продавца")
    history: List[NmReportHistory] = []


class DetailHistoryNmReportResponse(BaseModel):
    data: List[DetailHistoryNmReport] = []
    error: bool
    errorText: Optional[str]
    additionalErrors: Optional[List[NmReportResponseAdditionalError]]
