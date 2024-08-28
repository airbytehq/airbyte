#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import date, datetime
from decimal import Decimal
from typing import List

from .common import AddOn, CatalogModel
from .discount import Discount
from .transaction import Transaction


class Subscription(CatalogModel):
    add_ons: List[AddOn]
    balance: Decimal
    billing_day_of_month: Decimal
    billing_period_start_date: date
    billing_period_end_date: date
    created_at: datetime
    current_billing_cycle: Decimal
    days_past_due: Decimal
    description: str
    discounts: List[Discount]
    failure_count: Decimal
    first_billing_date: date
    id: str
    merchant_account_id: str
    never_expires: bool
    next_bill_amount: Decimal
    next_billing_date: date
    next_billing_period_amount: Decimal
    number_of_billing_cycles: Decimal
    paid_through_date: date
    payment_method_token: str
    plan_id: str
    price: Decimal
    status: str
    transactions: List[Transaction]
    trial_duration: Decimal
    trial_duration_unit: str
    trial_period: bool
    updated_at: datetime
