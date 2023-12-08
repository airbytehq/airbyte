#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from decimal import Decimal
from typing import Optional

from .common import AddOn, CatalogModel
from .discount import Discount


class Plan(CatalogModel):
    add_ons: list[AddOn]
    billing_day_of_month: Optional[Decimal]
    billing_frequency: Decimal
    created_at: datetime
    currency_iso_code: str
    description: str
    discounts: list[Discount]
    id: str
    name: str
    number_of_billing_cycles: Optional[Decimal]
    price: Decimal
    trial_duration: Decimal
    trial_duration_unit: str
    trial_period: bool
    updated_at: datetime
