from __future__ import annotations

from typing import Optional

from pydantic import Field, validator

from source_ozon.schemas.base_report_data import BaseOzonReport


class BannerReport(BaseOzonReport):
    banner: Optional[str] = Field(description="Баннер")
    page_type: Optional[str] = Field(description="Тип страницы")
    impression_condition: Optional[str] = Field(description="Условие показа")
    platform: Optional[str] = Field(description="Платформа")
    impressions: Optional[int] = Field(description="Показы")
    clicks: Optional[int] = Field(description="Клики")
    ctr: Optional[float] = Field(description="CTR (%)")
    coverage: Optional[float] = Field(description="Охват")
    avg_price_for_1000_impressions_rub: Optional[float] = Field(description="Ср. цена 1000 показов, ₽")
    expense_rub_with_vat: Optional[float] = Field(description="Расход, ₽, с НДС")

    @validator("ctr", "coverage", "avg_price_for_1000_impressions_rub", "expense_rub_with_vat", pre=True)
    def parse_float_field(cls, value: str | int | float) -> float:
        if isinstance(value, str):
            value = value.replace(",", ".")
        return float(value)
