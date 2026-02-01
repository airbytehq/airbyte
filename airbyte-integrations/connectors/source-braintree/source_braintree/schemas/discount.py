#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Optional

from .common import CatalogModel


class Discount(CatalogModel):
    amount: float
    current_billing_cycle: Optional[float]
    description: str
    id: str
    kind: str
    name: str
    never_expires: bool
    number_of_billing_cycles: Optional[float]
    quantity: Optional[float]
