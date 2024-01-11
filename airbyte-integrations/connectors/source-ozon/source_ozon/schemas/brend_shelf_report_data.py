from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import Field, validator

from source_ozon.schemas.base_report_data import BaseOzonReport


class BrandShelfReport(BaseOzonReport):
    date: Optional[date] = Field(description="Дата", alias="Дата")
    condition_type: Optional[str] = Field(description="Тип условия", alias="Тип условия")
    impression_condition: Optional[str] = Field(description="Условие показа", alias="Условие показа")
    platform: Optional[str] = Field(description="Платформа", alias="Платформа")
    impressions: Optional[int] = Field(description="Показы", alias="Показы")
    clicks: Optional[int] = Field(description="Клики", alias="Клики")
    ctr: Optional[float] = Field(description="CTR (%)", alias="CTR (%)")
    coverage: Optional[float] = Field(description="Охват", alias="Охват")
    avg_price_for_1000_impressions_rub: Optional[float] = Field(description="Ср. цена 1000 показов, ₽", alias="Ср. цена 1000 показов, ₽")
    expense_rub_with_vat: Optional[float] = Field(description="Расход, ₽, с НДС", alias="Расход, ₽, с НДС")

    @validator("ctr", "coverage", "avg_price_for_1000_impressions_rub", "expense_rub_with_vat", pre=True)
    def parse_float_field(cls, value: str | int | float | None) -> float | None:
        if not value:
            return
        if isinstance(value, str):
            value = value.replace(",", ".")
        return float(value)
