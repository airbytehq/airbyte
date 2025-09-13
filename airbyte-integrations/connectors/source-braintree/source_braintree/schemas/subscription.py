#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import date, datetime
from typing import List

from .common import AddOn, CatalogModel
from .discount import Discount
from .transaction import Transaction


class Subscription(CatalogModel):
    add_ons: List[AddOn]
    balance: float
    billing_day_of_month: float
    billing_period_start_date: date
    billing_period_end_date: date
    created_at: datetime
    current_billing_cycle: float
    days_past_due: float
    description: str
    discounts: List[Discount]
    failure_count: float
    first_billing_date: date
    id: str
    merchant_account_id: str
    never_expires: bool
    next_bill_amount: float
    next_billing_date: date
    next_billing_period_amount: float
    number_of_billing_cycles: float
    paid_through_date: date
    payment_method_token: str
    plan_id: str
    price: float
    status: str
    transactions: List[Transaction]
    trial_duration: float
    trial_duration_unit: str
    trial_period: bool
    updated_at: datetime
