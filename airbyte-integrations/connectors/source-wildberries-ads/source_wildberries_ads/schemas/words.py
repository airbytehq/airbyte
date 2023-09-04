from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class AdsWordKeyword(BaseModel):
    keyword: str = Field(description="Ключевая фраза")
    count: int = Field(description="Количество просмотров по ключевой фразе")


class AdsWord(BaseModel):
    phrase: Optional[List[str]] = Field(description="Фразовое соответствие (минус фразы)")
    strong: Optional[List[str]] = Field(description="Точное соответствие (минус фразы)")
    excluded: Optional[List[str]] = Field(description="Минус фразы из поиска")
    pluse: Optional[List[str]] = Field(description="Фиксированные фразы")
    keywords: Optional[List[AdsWordKeyword]] = Field(description="Блок со статистикой по ключевым фразам")
    fixed: bool = Field(description="Фиксированные ключевые фразы (true - включены, false - выключены)")


class AdsStat(BaseModel):
    # fmt: off
    advertId: Optional[int] = Field(description="Идентификатор РК в системе Wildberries")
    keyword: Optional[str] = Field(description="Ключевая фраза")
    campaignName: Optional[str] = Field(description="Название РК")
    begin: Optional[datetime] = Field(description="Дата запуска РК")
    end: Optional[datetime] = Field(description="Дата завершения РК")
    views: Optional[int] = Field(description="Количество просмотров")
    clicks: Optional[int] = Field(description="Количество кликов")
    frq: Optional[float] = Field(description="Частота (отношение количества просмотров к количеству уникальных пользователей)")
    ctr: Optional[float] = Field(description="Показатель кликабельности (отношение числа кликов к количеству показов. Выражается в процентах)")
    cpc: Optional[float] = Field(description="Стоимость клика, ₽")
    duration: Optional[int] = Field(description="Длительность РК, в секундах")
    sum: Optional[float] = Field(description="Затраты, ₽")
    # fmt: on


class AdsWordsStat(BaseModel):
    words: AdsWord = Field(description="Блок информации по ключевым фразам")
    stat: List[AdsStat] = Field(
        description="""Массив информации по статистике.
            Первый элемент массива с keyword: "Всего по кампании" содержит суммарную информацию по всем ключевым фразам.
            Каждый следующий элемент массива содержит информацию по отдельной ключевой фразе.
            Отображается 60 ключевых фраз с наибольшим количеством просмотров."""
    )
