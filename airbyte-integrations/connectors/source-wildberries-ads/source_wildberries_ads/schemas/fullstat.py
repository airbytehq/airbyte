from datetime import datetime, date

from pydantic import BaseModel, Field

from typing import Optional, List


class AdsDayAppNmStat(BaseModel):
    # fmt: off
    views: Optional[int] = Field(description="Количество просмотров")
    clicks: Optional[int] = Field(description="Количество кликов")
    ctr: Optional[float] = Field(description="Показатель кликабельности. Отношение числа кликов к количеству показов. Выражается в процентах.")
    cpc: Optional[float] = Field(description="Средняя стоимость клика, ₽")
    sum: Optional[float] = Field(description="Затраты, ₽")
    atbs: Optional[int] = Field(description="Количество добавлений товаров в корзину")
    orders: Optional[int] = Field(description="Количество заказов товара")
    cr: Optional[float] = Field(description="CR(conversion rate) — это отношение количества заказов к общему количеству посещений рекламной кампании.")
    shks: Optional[int] = Field(description="Заказано товаров, шт")
    sum_price: Optional[int] = Field(description="Заказов на сумму, ₽")
    name: Optional[str] = Field(description="Наименование товара")
    nmId: Optional[int] = Field(description="Артикул WB")
    # fmt: on


class AdsDayAppStat(BaseModel):
    # fmt: off
    views: Optional[int] = Field(description="Количество просмотров")
    clicks: Optional[int] = Field(description="Количество кликов")
    ctr: Optional[float] = Field(description="Показатель кликабельности. Отношение числа кликов к количеству показов")
    cpc: Optional[float] = Field(description="Средняя стоимость клика, ₽")
    sum: Optional[float] = Field(description="Затраты, ₽")
    atbs: Optional[int] = Field(description="Количество добавлений товаров в корзину")
    orders: Optional[int] = Field(description="Количество заказов товара")
    cr: Optional[float] = Field(description="CR(conversion rate) — это отношение количества заказов к общему количеству посещений рекламной кампании")
    shks: Optional[int] = Field(description="Заказано товаров, шт")
    sum_price: Optional[float] = Field(description="Заказов на сумму, ₽")
    nm: Optional[List[AdsDayAppNmStat]] = Field(description="Блок статистики по артикулам WB")
    appType: Optional[int] = Field(description="Тип платформы (1 - сайт, 32 - Android, 64 - IOS)")
    # fmt: on


class AdsDayStat(BaseModel):
    # fmt: off
    date: Optional[datetime] = Field(description="Дата, за которую представлены данные")
    views: Optional[int] = Field(description="Количество просмотров")
    clicks: Optional[int] = Field(description="Количество кликов")
    ctr: Optional[float] = Field(description="Показатель кликабельности. Отношение числа кликов к количеству показов. Выражается в процентах.")
    cpc: Optional[float] = Field(description="Средняя стоимость клика, ₽")
    sum: Optional[float] = Field(description="Затраты, ₽")
    atbs: Optional[int] = Field(description="Количество добавлений товаров в корзину")
    orders: Optional[int] = Field(description="Количество заказов товара")
    cr: Optional[float] = Field(description="CR(conversion rate) — это отношение количества заказов к общему количеству посещений рекламной кампании")
    shks: Optional[int] = Field(description="Заказано товаров, шт")
    sum_price: Optional[float] = Field(description="Заказов на сумму, ₽")
    apps: Optional[List[AdsDayAppStat]] = Field(description="Блок информации о платформе")
    # fmt: on


class AdsFullBoosterStat(BaseModel):
    date: Optional[datetime] = Field(description="Дата, за которую предоставлены данные")
    nm: Optional[int] = Field(description="Артикул WB")
    avg_position: Optional[int] = Field(description="Средняя позиция товара на страницах поисковой выдачи и каталога")


class AdsFullStatInterval(BaseModel):
    begin: Optional[date] = Field(description="Начало запрашиваемого периода")
    end: Optional[date] = Field(description="Конец запрашиваемого периода")


class AdsFullStat(BaseModel):
    # fmt: off
    interval: Optional[AdsFullStatInterval] = Field(description="Запрошенный временной диапазон")
    views: Optional[int] = Field(description="Количество просмотров. За все дни запрошенного диапазона, по всем артикулам WB и платформам.")
    clicks: Optional[int] = Field(description="Количество кликов. За все дни запрошенного диапазона, по всем артикулам WB и платформам.")
    ctr: Optional[float] = Field(description="Показатель кликабельности. Отношение числа кликов к количеству показов. Выражается в процентах. За все дни запрошенного диапазона, по всем артикулам WB и платформам.")
    cpc: Optional[float] = Field(description="Средняя стоимость клика, ₽. За все дни запрошенного диапазона, по всем артикулам WB и платформам.")
    sum: Optional[float] = Field(description="Затраты, ₽. За все дни запрошенного диапазона, по всем артикулам WB и платформам.")
    atbs: Optional[int] = Field(description="Количество добавлений товаров в корзину. а все дни запрошенного диапазона, по всем артикулам WB и платформам.")
    orders: Optional[int] = Field(description="Количество заказов товара. За все дни запрошенного диапазона, по всем артикулам WB и платформам.")
    cr: Optional[float] = Field(description="CR(conversion rate) — это отношение количества заказов к общему количеству посещений рекламной кампании. За все дни запрошенного диапазона, по всем артикулам WB и платформам.")
    shks: Optional[int] = Field(description="Заказано товаров, шт. За все дни запрошенного диапазона, по всем артикулам WB и платформам.")
    sum_price: Optional[float] = Field(description="Заказов на сумму, ₽. За все дни запрошенного диапазона, по всем артикулам WB и платформам.")
    days: Optional[List[AdsDayStat]] = Field(description="Блок статистики по дням")
    boosterStats: Optional[List[AdsFullBoosterStat]] = Field(description="Статистика по средней позиции товара на страницах поисковой выдачи и каталога (для автоматических кампаний).")
    advertId: Optional[int] = Field(description="ID кампании")
    # fmt: on
