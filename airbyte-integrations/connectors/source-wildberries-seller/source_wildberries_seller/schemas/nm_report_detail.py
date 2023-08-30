from typing import Optional, List

from pydantic import BaseModel, Field

from source_wildberries_seller.schemas.common import (
    NmReportResponseAdditionalError,
    NmReportTag,
    NmReportObject,
    NmReportStatistics,
)


class DetailNmReportStocks(BaseModel):
    stocksMp: Optional[int] = Field(description="Остатки МП, шт. (Общее количество остатков на складе продавца)")
    stocksWb: Optional[int] = Field(description="Остатки на складах Wildberries (Общее количество остатков на складах Wildberries)")


class DetailNmReport(BaseModel):
    nmID: Optional[int] = Field(description="Артикул WB")
    vendorCode: Optional[str] = Field(description="Артикул продавца")
    brandName: Optional[str] = Field(description="Название бренда")
    tags: List[NmReportTag] = Field(description="Теги", default=[])
    object: Optional[NmReportObject] = Field(description="Предмет")
    statistics: Optional[NmReportStatistics] = Field(description="Статистика")
    stocks: Optional[DetailNmReportStocks] = Field(description="Остатки")


class DetailNmReportResponseData(BaseModel):
    page: int
    isNextPage: bool
    cards: List[DetailNmReport] = []


class DetailNmReportResponse(BaseModel):
    data: DetailNmReportResponseData
    error: bool
    errorText: Optional[str]
    additionalErrors: Optional[List[NmReportResponseAdditionalError]]
