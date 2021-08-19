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
from typing import List, Optional

from .cards import (
    Address,
    AndroidPayCard,
    ApplePayCard,
    CreditCard,
    MasterpassCard,
    PaymentMethod,
    PayPalAccount,
    SamsungPayCard,
    USBankAccount,
    VenmoAccount,
    VisaCheckoutCard,
)
from .common import CatalogModel


class Customer(CatalogModel):
    addresses: List[Address]
    android_pay_cards: Optional[List[AndroidPayCard]]
    apple_pay_cards: Optional[List[ApplePayCard]]
    company: str
    created_at: datetime
    credit_cards: Optional[List[CreditCard]]
    custom_fields: str
    email: str
    fax: str
    first_name: str
    graphql_id: str
    id: str
    last_name: str
    masterpass_cards: List[MasterpassCard]
    payment_methods: List[PaymentMethod]
    paypal_accounts: List[PayPalAccount]
    phone: str
    samsung_pay_cards: List[SamsungPayCard]
    updated_at: datetime
    us_bank_accounts: List[USBankAccount]
    venmo_accounts: List[VenmoAccount]
    visa_checkout_cards: List[VisaCheckoutCard]
    website: str
