from __future__ import annotations

from typing import Optional

from pydantic import Field, validator

from source_ozon.schemas.base_report_data import BaseOzonReport


class SkuReport(BaseOzonReport):
    sku: Optional[str] = Field(description="SKU")
    product_name: Optional[str] = Field(description="Название товара")
    product_price_rub: Optional[float] = Field(description="Цена товара, ₽")
    impressions: Optional[int] = Field(description="Показы")
    clicks: Optional[int] = Field(description="Клики")
    ctr: Optional[float] = Field(description="CTR (%)")
    conversion: Optional[float] = Field(description="Конверсия")
    avg_click_price_rub: Optional[float] = Field(description="Ср. цена клика, ₽")
    expense_with_vat: Optional[float] = Field(description="Расход, ₽, с НДС")
    orders: Optional[int] = Field(description="Заказы")
    revenue_rub: Optional[float] = Field(description="Выручка, ₽")
    model_orders: Optional[int] = Field(description="Заказы модели")
    model_orders_revenue_rub: Optional[float] = Field(description="Выручка с заказов модели, ₽")

    @validator(
        "product_price_rub",
        "ctr",
        "conversion",
        "avg_click_price_rub",
        "expense_with_vat",
        "revenue_rub",
        "model_orders_revenue_rub",
        pre=True,
    )
    def parse_float_field(cls, value: str | int | float) -> float:
        if isinstance(value, str):
            value = value.replace(",", ".")
        return float(value)
