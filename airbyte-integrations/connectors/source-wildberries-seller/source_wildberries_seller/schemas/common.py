from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class NmReportResponseAdditionalError(BaseModel):
    field: str
    description: str


class NmReportTag(BaseModel):
    id: int = Field(description="Идентификатор тега")
    name: Optional[str] = Field(description="Название тега")


class NmReportObject(BaseModel):
    id: int = Field(description="Идентификатор предмета")
    name: Optional[str] = Field(description="Название предмета")


class NmReportStatisticsPeriodConversion(BaseModel):
    # fmt: off
    addToCartPercent: Optional[int] = Field(description="Конверсия в корзину, % (Какой процент посетителей, открывших карточку товара, добавили товар в корзину)")
    cartToOrderPercent: Optional[int] = Field(description="Конверсия в заказ, % (Какой процент посетителей, добавивших товар в корзину, сделали заказ)")
    buyoutsPercent: Optional[int] = Field(description="Процент выкупа, % (Какой процент посетителей, заказавших товар, его выкупили. Без учета товаров, которые еще доставляются покупателю)")
    # fmt: on


class NmReportStatisticsPeriod(BaseModel):
    begin: Optional[str] = Field(description="Начало периода")
    end: Optional[str] = Field(description="Конец периода")
    openCardCount: Optional[int] = Field(description="Количество переходов в карточку товара")
    addToCartCount: Optional[int] = Field(description="Положили в корзину, штук")
    ordersCount: Optional[int] = Field(description="Заказали товаров, шт")
    ordersSumRub: Optional[int] = Field(description="Заказали на сумму, руб.")
    buyoutsCount: Optional[int] = Field(description="Выкупили товаров, шт.")
    buyoutsSumRub: Optional[int] = Field(description="Выкупили на сумму, руб.")
    cancelCount: Optional[int] = Field(description="Отменили товаров, шт.")
    cancelSumRub: Optional[int] = Field(description="Отменили на сумму, руб.")
    avgPriceRub: Optional[int] = Field(description="Средняя цена, руб.")
    avgOrdersCountPerDay: Optional[int] = Field(description="Среднее количество заказов в день, шт.")
    conversions: Optional[NmReportStatisticsPeriodConversion] = Field(description="Конверсии")


class NmReportStatisticsPeriodComparison(BaseModel):
    openCardDynamics: Optional[int] = Field(description="Динамика переходов в карточку товара")
    addToCartDynamics: Optional[int] = Field(description="Динамика добавлений в корзину")
    ordersCountDynamics: Optional[int] = Field(description="Динамика количества заказов")
    ordersSumRubDynamics: Optional[int] = Field(description="Динамика суммы заказов, рублей")
    buyoutsCountDynamics: Optional[int] = Field(description="Динамика выкупов, штук")
    buyoutsSumRubDynamics: Optional[int] = Field(description="Динамика суммы выкупов, рублей")
    cancelCountDynamics: Optional[int] = Field(description="Динамика отмен товаров, штук")
    cancelSumRubDynamics: Optional[int] = Field(description="Динамика сумм отмен товаров, рублей")
    avgOrdersCountPerDayDynamics: Optional[int] = Field(description="Динамика среднего количества заказов в день")
    avgPriceRubDynamics: Optional[int] = Field(description="Динамика средней цены на товары. Учитываются скидки для акций и WB скидка")
    conversions: Optional[NmReportStatisticsPeriodConversion] = Field(description="Конверсии")


class NmReportStatistics(BaseModel):
    selectedPeriod: Optional[NmReportStatisticsPeriod] = Field(description="Запрашиваемый период")
    previousPeriod: Optional[NmReportStatisticsPeriod] = Field(description="Статистика за предыдущие 30 дней")
    periodComparison: Optional[NmReportStatisticsPeriodComparison] = Field(description="Сравнение двух периодов, в процентах")


class NmReportHistory(BaseModel):
    # fmt: off
    dt: Optional[date]
    openCardCount: Optional[int] = Field(description="Количество переходов в карточку товара")
    addToCartCount: Optional[int] = Field(description="Положили в корзину, штук")
    ordersCount: Optional[int] = Field(description="Заказали товаров, шт")
    ordersSumRub: Optional[int] = Field(description="Заказали на сумму, руб.")
    buyoutsCount: Optional[int] = Field(description="Выкупили товаров, шт.")
    buyoutsSumRub: Optional[int] = Field(description="Выкупили на сумму, руб.")
    buyoutPercent: Optional[int] = Field(description="Процент выкупа, % (Какой процент посетителей, заказавших товар, его выкупили. Без учета товаров, которые еще доставляются покупателю)")
    addToCartConversion: Optional[int] = Field(description="Конверсия в корзину, % (Какой процент посетителей, открывших карточку товара, добавили товар в корзину)")
    cartToOrderConversion: Optional[int] = Field(description="Конверсия в заказ, % (Какой процент поситителей, добавивших товар в корзину, сделали заказ)")
    # fmt: on
