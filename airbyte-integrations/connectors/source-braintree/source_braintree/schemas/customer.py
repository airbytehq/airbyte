#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from typing import Optional

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
    addresses: list[Address]
    android_pay_cards: Optional[list[AndroidPayCard]]
    apple_pay_cards: Optional[list[ApplePayCard]]
    company: str
    created_at: datetime
    credit_cards: Optional[list[CreditCard]]
    custom_fields: str
    email: str
    fax: str
    first_name: str
    graphql_id: str
    id: str
    last_name: str
    masterpass_cards: list[MasterpassCard]
    payment_methods: list[PaymentMethod]
    paypal_accounts: list[PayPalAccount]
    phone: str
    samsung_pay_cards: list[SamsungPayCard]
    updated_at: datetime
    us_bank_accounts: list[USBankAccount]
    venmo_accounts: list[VenmoAccount]
    visa_checkout_cards: list[VisaCheckoutCard]
    website: str
