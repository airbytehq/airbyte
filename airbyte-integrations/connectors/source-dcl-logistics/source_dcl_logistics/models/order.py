#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class Order(BaseModel):
    account_number: str
    order_number: str
    item_number: str
    serial_number: str
    ship_date: Optional[date] = None
    quantity: Optional[int] = 0
    customer_number: Optional[str] = None
    description: Optional[str] = None
    email: Optional[str] = None
    country: Optional[str] = None
    state_province: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    company: Optional[str] = None
    attention: Optional[str] = None
    carton_id: Optional[str] = None
    order_type: Optional[str] = None
    tracking_number: Optional[str] = None
    updated_at: datetime
