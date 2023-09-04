from datetime import date as dt_date
from typing import Optional, List

from pydantic import BaseModel, Field


class AdsSeaCatDaySeaCatStat(BaseModel):
    views: Optional[int] = Field(description="Количество просмотров")
    clicks: Optional[int] = Field(description="Количество кликов")
    orders: Optional[int] = Field(description="Количество заказов")
    sum: Optional[float] = Field(description="Затраты, ₽")


class AdsSeaCatDayStat(BaseModel):
    date: Optional[dt_date] = Field(description="Дата")
    search: Optional[AdsSeaCatDaySeaCatStat] = Field(description="Поиск")
    catalog: Optional[AdsSeaCatDaySeaCatStat] = Field(description="Каталог")


class AdsSeaCatStat(BaseModel):
    totalViews: Optional[int] = Field(description="Суммарное количество просмотров")
    totalClicks: Optional[int] = Field(description="Суммарное количество кликов")
    totalOrders: Optional[int] = Field(description="Суммарное количество заказов")
    totalSum: Optional[float] = Field(description="Суммарные затраты, ₽")
    dates: Optional[List[AdsSeaCatDayStat]] = Field(description="Блок статистики")
