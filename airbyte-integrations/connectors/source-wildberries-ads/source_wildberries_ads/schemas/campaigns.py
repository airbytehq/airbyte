from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AdsCampaign(BaseModel):
    advertId: int = Field(description="Идентификатор кампании")
    type: int = Field(
        description=(
            "Тип кампании: "
            "4 - кампания в каталоге, "
            "5 - кампания в карточке товара, "
            "6 - кампания в поиске, "
            "7 - кампания в рекомендациях на главной странице, "
            "8 - автоматическая кампания, "
            "9 - поиск + каталог"
        )
    )
    status: int = Field(
        description=(
            "Статус кампании: "
            "-1 - кампания в процессе удаления"
            "4 - готова к запуску, "
            "7 - кампания завершена, "
            "8 - отказался, "
            "9 - идут показы, "
            "11 - кампания на паузе"
        )
    )
    dailyBudget: float = Field(description="Сумма дневного бюджета")
    createTime: datetime = Field(description="Время создания кампании")
    changeTime: Optional[str] = Field(description="Время последнего изменения кампании")
    startTime: Optional[str] = Field(description="Дата запуска кампании")
    endTime: Optional[str] = Field(description="Дата завершения кампании")
    name: Optional[str] = Field(description="Название кампании")
