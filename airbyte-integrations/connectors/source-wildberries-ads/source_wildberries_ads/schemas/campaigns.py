from datetime import datetime

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
            "4 - готова к запуску, "
            "7 - кампания завершена, "
            "8 - отказался, "
            "9 - идут показы, "
            "11 - кампания на паузе"
        )
    )
    dailyBudget: float = Field(description="Сумма дневного бюджета")
    createTime: datetime = Field(description="Время создания кампании")
    changeTime: str = Field(description="Время последнего изменения кампании")
    startTime: str = Field(description="Время последнего запуска кампании")
    endTime: str = Field(description="Время завершения кампании (state 7)")
