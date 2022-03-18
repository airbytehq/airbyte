#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field
from typing_extensions import Annotated


class Order(BaseModel):
    account_number: Annotated[str, Field(max_length=256)]
    order_number: Annotated[str, Field(max_length=256)]
    item_number: Annotated[str, Field(max_length=256)]
    serial_number: Annotated[str, Field(max_length=256)]
    ship_date: Optional[date] = None
    quantity: Optional[int] = 0
    customer_number: Annotated[Optional[str], Field(max_length=256)] = None
    description: Annotated[Optional[str], Field(max_length=2048)] = None
    email: Annotated[Optional[str], Field(max_length=256)] = None
    country: Annotated[Optional[str], Field(max_length=256)] = None
    state_province: Annotated[Optional[str], Field(max_length=256)] = None
    city: Annotated[Optional[str], Field(max_length=256)] = None
    postal_code: Annotated[Optional[str], Field(max_length=256)] = None
    company: Annotated[Optional[str], Field(max_length=256)] = None
    attention: Annotated[Optional[str], Field(max_length=1024)] = None
    carton_id: Annotated[Optional[str], Field(max_length=256)] = None
    order_type: Annotated[Optional[str], Field(max_length=256)] = None
    tracking_number: Annotated[Optional[str], Field(max_length=256)] = None
    updated_at: datetime
