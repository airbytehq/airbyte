from typing import Optional

from pydantic import BaseModel, Field


class PriceStatistics(BaseModel):
    nmId: Optional[int] = Field(description="Артикул WB")
    price: Optional[float] = Field(description="Цена")
    discount: Optional[float] = Field(description="Скидка")
    promoCode: Optional[float] = Field(description="Промокод")
