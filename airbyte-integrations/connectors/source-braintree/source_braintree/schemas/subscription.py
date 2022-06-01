#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from decimal import Decimal
from typing import List

from .common import AddOn, CatalogModel
from .discount import Discount
from .transaction import Transaction


class Subscription(CatalogModel):
    add_ons: List[AddOn]
    balance: Decimal
    billing_day_of_month: Decimal
    billing_period_start_date: datetime
    created_at: datetime
    current_billing_cycle: Decimal
    days_past_due: Decimal
    description: str
    discounts: List[Discount]
    failure_count: Decimal
    first_billing_date: datetime
    id: str
    merchant_account_id: str
    never_expires: bool
    next_bill_amount: Decimal
    next_billing_date: datetime
    next_billing_period_amount: Decimal
    number_of_billing_cycles: Decimal
    paid_through_date: datetime
    payment_method_token: str
    plan_id: str
    price: Decimal
    status: str
    transactions: List[Transaction]
    trial_duration: Decimal
    trial_duration_unit: str
    trial_period: bool
    updated_at: datetime
