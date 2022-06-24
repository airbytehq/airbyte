#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Union

from .common import AllOptional, CatalogModel


class Evidence(CatalogModel, metaclass=AllOptional):
    created_at: datetime
    id: str
    sent_to_processor_at: datetime
    url: str
    comment: str


class PaypalMessage(CatalogModel):
    message: str
    send_at: datetime
    sender: str


class Dispute(CatalogModel):
    amount_disputed: Decimal
    amount_won: Decimal
    case_number: str
    chargeback_protection_level: Optional[str]
    created_at: datetime
    currency_iso_code: str
    evidence: Union[Evidence, List[Evidence]]
    graphql_id: str
    id: str
    kind: str
    merchant_account_id: str
    original_dispute_id: Optional[str]
    paypal_messages: List[PaypalMessage]
    processor_comments: Optional[str]
    reason: str
    reason_code: str
    reason_description: Optional[str]
    received_date: date
    reference_number: Optional[str]
    reply_by_date: date
    status: str
    updated_at: datetime
