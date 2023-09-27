from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AdsCostHistoryStat(BaseModel):
    # fmt: off
    updNum: Optional[int] = Field(description="Номер выставленного документа (при наличии)")
    updTime: Optional[datetime] = Field(description="Время списания")
    updSum: Optional[float] = Field(description="Выставленная сумма")
    advertId: Optional[int] = Field(description="Идентификатор кампании")
    campName: Optional[str] = Field(description="Название кампании")
    advertType: Optional[int] = Field(description="Тип кампании")
    paymentType: Optional[str] = Field(description="Источник списания")
    advertStatus: Optional[int] = Field(description="Статус кампании: 4 - готова к запуску, 7 - завершена, 8 - отказался, 9 - активна, 11 - приостановлена")
    # fmt: on
