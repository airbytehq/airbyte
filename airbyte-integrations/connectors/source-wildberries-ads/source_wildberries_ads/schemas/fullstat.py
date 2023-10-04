from datetime import datetime

from pydantic import BaseModel, Field

from typing import Optional, List


class AdsDayAppNmStat(BaseModel):
    # fmt: off
    nmId: Optional[int] = Field(description="Артикул WB")
    name: Optional[str] = Field(description="Наименование товара")
    views: Optional[int] = Field(description="Количество просмотров")
    clicks: Optional[int] = Field(description="Количество кликов")
    frq: Optional[float] = Field(description="Частота (отношение количества просмотров к количеству уникальных пользователей)")
    unique_users: Optional[int] = Field(description="Количество уникальных пользователей просмотревших товар")
    ctr: Optional[float] = Field(description="Показатель кликабельности. Отношение числа кликов к количеству показов. Выражается в процентах.")
    cpc: Optional[float] = Field(description="Средняя стоимость клика, ₽")
    sum: Optional[float] = Field(description="Затраты, ₽")
    atbs: Optional[int] = Field(description="Количество добавлений товаров в корзину")
    orders: Optional[int] = Field(description="Количество заказов товара")
    cr: Optional[float] = Field(description="CR(conversion rate) — это отношение количества заказов к общему количеству посещений рекламной кампании.")
    shks: Optional[int] = Field(description="Заказано товаров, шт")
    sum_price: Optional[int] = Field(description="Заказов на сумму, ₽")
    # fmt: on


class AdsDayAppStat(BaseModel):
    # fmt: off
    appType: Optional[int] = Field(description="Тип платформы (1 - сайт, 32 - Android, 64 - IOS)")
    nm: Optional[List[AdsDayAppNmStat]] = Field(description="Блок статистики по артикулам WB")
    views: Optional[int] = Field(description="Количество просмотров. В целом по платформе.")
    clicks: Optional[int] = Field(description="Количество кликов. В целом по платформе.")
    frq: Optional[float] = Field(description="Частота (отношение количества просмотров к количеству уникальных пользователей). В целом по платформе.")
    unique_users: Optional[int] = Field(description="Количество уникальных пользователей просмотревших товар. В целом по платформе.")
    ctr: Optional[float] = Field(description="Показатель кликабельности. Отношение числа кликов к количеству показов. Выражается в процентах. В целом по платформе.")
    cpc: Optional[float] = Field(description="Средняя стоимость клика, ₽. В целом по платформе.")
    sum: Optional[float] = Field(description="Затраты, ₽. В целом по платформе.")
    atbs: Optional[int] = Field(description="Количество добавлений товаров в корзину. В целом по платформе.")
    orders: Optional[int] = Field(description="Количество заказов товара. В целом по платформе.")
    cr: Optional[float] = Field(description="CR(conversion rate) — это отношение количества заказов к общему количеству посещений рекламной кампании. В целом по платформе.")
    shks: Optional[int] = Field(description="Заказано товаров, шт. В целом по платформе.")
    sum_price: Optional[float] = Field(description="Заказов на сумму, ₽. В целом по платформе.")
    # fmt: on


class AdsDayStat(BaseModel):
    # fmt: off
    date: Optional[datetime] = Field(description="Дата генерации блока данных. В блоке отображаются статистические данные за эту дату.")
    apps: Optional[List[AdsDayAppStat]] = Field(description="Блок информации о платформе")
    views: Optional[int] = Field(description="Количество просмотров. За день, по всем артикулам WB и платформам.")
    clicks: Optional[int] = Field(description="Количество кликов. За день, по всем артикулам WB и платформам.")
    frq: Optional[float] = Field(description="Частота (отношение количества просмотров к количеству уникальных пользователей). За день, по всем артикулам WB и платформам.")
    unique_users: Optional[int] = Field(description="Количество уникальных пользователей просмотревших товар. За день, по всем артикулам WB и платформам.")
    ctr: Optional[float] = Field(description="Показатель кликабельности. Отношение числа кликов к количеству показов. Выражается в процентах. За день, по всем артикулам WB и платформам.")
    cpc: Optional[float] = Field(description="Средняя стоимость клика, ₽. За день, по всем артикулам WB и платформам.")
    sum: Optional[float] = Field(description="Затраты, ₽. За день, по всем артикулам WB и платформам.")
    atbs: Optional[int] = Field(description="Количество добавлений товаров в корзину. За день, по всем артикулам WB и платформам.")
    orders: Optional[int] = Field(description="Количество заказов товара. За день, по всем артикулам WB и платформам.")
    cr: Optional[float] = Field(description="CR(conversion rate) — это отношение количества заказов к общему количеству посещений рекламной кампании. За день, по всем артикулам WB и платформам.")
    shks: Optional[int] = Field(description="Заказано товаров, шт. За день, по всем артикулам WB и платформам.")
    sum_price: Optional[float] = Field(description="Заказов на сумму, ₽. За день, по всем артикулам WB и платформам.")
    # fmt: on


class AdsFullBoosterStat(BaseModel):
    date: Optional[datetime] = Field(description="Дата, за которую предоставлены данные.")
    nm: Optional[int] = Field(description="Артикул WB")
    avg_position: Optional[int] = Field(description="Средняя позиция товара на страницах поисковой выдачи и каталога.")


class AdsFullStat(BaseModel):
    # fmt: off
    advertId: Optional[int] = Field(description="ID рекламной кампании")
    begin: Optional[datetime] = Field(description="Дата запуска РК")
    end: Optional[datetime] = Field(description="Дата остановки РК")
    days: Optional[List[AdsDayStat]] = Field(description="Блок статистики по дням")
    views: Optional[int] = Field(description="Количество просмотров. За все дни, по всем артикулам WB и платформам.")
    clicks: Optional[int] = Field(description="Количество кликов. За все дни, по всем артикулам WB и платформам.")
    frq: Optional[float] = Field(description="Частота (отношение количества просмотров к количеству уникальных пользователей). За все дни, по всем артикулам WB и платформам.")
    unique_users: Optional[int] = Field(description="Количество уникальных пользователей просмотревших товар. За все дни, по всем артикулам WB и платформам.")
    ctr: Optional[float] = Field(description="Показатель кликабельности. Отношение числа кликов к количеству показов. Выражается в процентах. За все дни, по всем артикулам WB и платформам.")
    cpc: Optional[float] = Field(description="Средняя стоимость клика, ₽. За все дни, по всем артикулам WB и платформам.")
    sum: Optional[float] = Field(description="Затраты, ₽. За все дни, по всем артикулам WB и платформам.")
    atbs: Optional[int] = Field(description="Количество добавлений товаров в корзину. За все дни, по всем артикулам WB и платформам.")
    orders: Optional[int] = Field(description="Количество заказов товара. За все дни, по всем артикулам WB и платформам.")
    cr: Optional[float] = Field(description="CR(conversion rate) — это отношение количества заказов к общему количеству посещений рекламной кампании. За все дни, по всем артикулам WB и платформам.")
    shks: Optional[int] = Field(description="Заказано товаров, шт. За все дни, по всем артикулам WB и платформам.")
    sum_price: Optional[float] = Field(description="Заказов на сумму, ₽. За все дни, по всем артикулам WB и платформам.")
    boosterStats: Optional[List[AdsFullBoosterStat]] = Field(description="Статистика по средней позиции товара на страницах поисковой выдачи и каталога (для автоматических кампаний).")
    # fmt: on
