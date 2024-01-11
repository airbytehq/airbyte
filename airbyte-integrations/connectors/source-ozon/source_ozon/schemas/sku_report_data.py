from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import Field, validator

from source_ozon.schemas.base_report_data import BaseOzonReport


class SkuReport(BaseOzonReport):
    date: Optional[date] = Field(description="Дата", alias="Дата")
    sku: Optional[str] = Field(description="SKU", alias="sku")
    product_name: Optional[str] = Field(description="Название товара", alias="Название товара")
    product_price_rub: Optional[float] = Field(description="Цена товара, ₽", alias="Цена товара, ₽")
    impressions: Optional[int] = Field(description="Показы", alias="Показы")
    clicks: Optional[int] = Field(description="Клики", alias="Клики")
    ctr: Optional[float] = Field(description="CTR (%)", alias="CTR (%)")
    conversion: Optional[float] = Field(description="Конверсия", alias="Конверсия")
    avg_click_price_rub: Optional[float] = Field(description="Ср. цена клика, ₽", alias="Ср. цена клика, ₽")
    expense_with_vat: Optional[float] = Field(description="Расход, ₽, с НДС", alias="Расход, ₽, с НДС")
    expense_without_bonuses: Optional[float] = Field(
        description="Расход за минусом бонусов, ₽, с НДС", alias="Расход за минусом бонусов, ₽, с НДС"
    )
    orders: Optional[int] = Field(description="Заказы", alias="Заказы")
    revenue_rub: Optional[float] = Field(description="Выручка, ₽", alias="Выручка, ₽")
    model_orders: Optional[int] = Field(description="Заказы модели", alias="Заказы модели")
    model_orders_revenue_rub: Optional[float] = Field(description="Выручка с заказов модели, ₽", alias="Выручка с заказов модели, ₽")

    @validator(
        "product_price_rub",
        "ctr",
        "conversion",
        "avg_click_price_rub",
        "expense_with_vat",
        "expense_without_bonuses",
        "revenue_rub",
        "model_orders_revenue_rub",
        pre=True,
    )
    def parse_float_field(cls, value: str | int | float | None) -> float | None:
        if not value:
            return
        if isinstance(value, str):
            value = value.replace(",", ".")
        return float(value)
