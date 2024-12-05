#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
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
