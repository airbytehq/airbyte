#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from typing import List, Optional

from .common import AddOn, CatalogModel
from .discount import Discount


class Plan(CatalogModel):
    add_ons: List[AddOn]
    billing_day_of_month: Optional[float]
    billing_frequency: float
    created_at: datetime
    currency_iso_code: str
    description: str
    discounts: List[Discount]
    id: str
    name: str
    number_of_billing_cycles: Optional[float]
    price: float
    trial_duration: float
    trial_duration_unit: str
    trial_period: bool
    updated_at: datetime
