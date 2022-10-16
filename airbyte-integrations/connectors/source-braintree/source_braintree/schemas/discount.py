#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from decimal import Decimal
from typing import Optional

from .common import CatalogModel


class Discount(CatalogModel):
    amount: Decimal
    current_billing_cycle: Optional[Decimal]
    description: str
    id: str
    kind: str
    name: str
    never_expires: bool
    number_of_billing_cycles: Optional[Decimal]
    quantity: Optional[Decimal]
