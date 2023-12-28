from __future__ import annotations

from datetime import datetime, date
from typing import Optional

from pydantic import Field, validator

from source_ozon.schemas.base_report_data import BaseOzonReport


class SearchPromoReport(BaseOzonReport):
    date: Optional[date] = Field(description="Дата", alias="Дата")
    order_id: Optional[str] = Field(description="ID заказа", alias="ID заказа")
    order_number: Optional[str] = Field(description="Номер заказа", alias="Номер заказа")
    ozon_id: Optional[str] = Field(description="Ozon ID", alias="Ozon ID")
    promoted_product_ozon_id: Optional[str] = Field(description="Ozon ID продвигаемого товара", alias="Ozon ID продвигаемого товара")
    article: Optional[str] = Field(description="Артикул", alias="Артикул")
    name: Optional[str] = Field(description="Наименование", alias="Наименование")
    quantity: Optional[float] = Field(description="Количество", alias="Количество")
    sale_price: Optional[float] = Field(description="Цена продажи", alias="Цена продажи")
    price_rub: Optional[float] = Field(description="Стоимость, ₽", alias="Стоимость, ₽")
    rate_percent: Optional[float] = Field(description="Ставка, %", alias="Ставка, %")
    rate_rub: Optional[float] = Field(description="Ставка, ₽", alias="Ставка, ₽")
    expense_rub: Optional[float] = Field(description="Расход, ₽", alias="Расход, ₽")

    @validator("date", pre=True)
    def parse_date_field(cls, value: str | date | datetime) -> date:
        if isinstance(value, str):
            return datetime.strptime(value, "%d.%m.%Y")
        return value

    @validator("quantity", "sale_price", "price_rub", "rate_percent", "rate_rub", "expense_rub", pre=True)
    def parse_float_field(cls, value: str | int | float | None) -> float | None:
        if not value:
            return
        if isinstance(value, str):
            value = value.replace(",", ".")
        return float(value)
