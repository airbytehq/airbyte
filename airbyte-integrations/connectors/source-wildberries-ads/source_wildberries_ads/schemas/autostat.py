from typing import Optional

from pydantic import BaseModel, Field


class AdsAutoStat(BaseModel):
    # fmt: off
    views: Optional[int] = Field(description="Количество просмотров")
    clicks: Optional[int] = Field(description="Количество кликов")
    ctr: Optional[float] = Field(description="CTR (Click-Through Rate) — показатель кликабельности. Отношение числа кликов к количеству показов. Выражается в процентах.")
    cpc: Optional[float] = Field(description="CPC(от англ. cost per click — цена за клик) — это цена клика по рекламному товару.")
    spend: Optional[float] = Field(description="Затраты, ₽")
    # fmt: on
