#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
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
