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

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

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
    evidence: Evidence
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
