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
from typing import Union

from .common import CatalogModel


class Address(CatalogModel):
    company: str
    country_code_alpha2: str
    country_code_alpha3: str
    country_code_numeric: str
    country_name: str
    created_at: datetime
    customer_id: str
    extended_address: str
    first_name: str
    id: str
    last_name: str
    locality: str
    postal_code: str
    region: str
    street_address: str
    updated_at: datetime


class CreditCard(CatalogModel):
    """
    https://developer.paypal.com/braintree/docs/reference/response/credit-card
    """

    billing_address: Address
    bin: str
    card_type: str
    cardholder_name: str
    commercial: str
    country_of_issuance: str
    created_at: datetime
    customer_id: str
    customer_location: str
    debit: str
    default: bool
    durbin_regulated: str
    expiration_date: str
    expiration_month: str
    expiration_year: str
    expired: bool
    healthcare: str
    image_url: str
    issuing_bank: str
    last_4: str
    masked_number: str
    payroll: str
    prepaid: str
    product_id: str
    token: str
    unique_number_identifier: str
    updated_at: datetime


class ApplePayCard(CreditCard):
    """
    https://developer.paypal.com/braintree/docs/reference/response/apple-pay-card
    """

    source_description: str
    payment_instrument_name: str


class SamsungPayCard(CreditCard):
    """
    https://developer.paypal.com/braintree/docs/reference/response/samsung-pay-card
    """


class MasterpassCard(CreditCard):
    """
    https://developer.paypal.com/braintree/docs/reference/response/masterpass-card
    """


class AndroidPayCard(CreditCard):
    """
    https://developer.paypal.com/braintree/docs/reference/response/android-pay-card
    """

    google_transaction_id: str
    source_card_type: str
    source_description: str
    is_network_tokenized: bool
    source_card_last_4: str
    source_card_type: str
    virtual_card_last_4: str
    virtual_card_type: str


class VisaCheckoutCard(CreditCard):
    """
    https://developer.paypal.com/braintree/docs/reference/response/visa-checkout-card
    """


class VenmoAccount(CreditCard):
    """
    https://developer.paypal.com/braintree/docs/reference/response/venmo-account
    """

    source_description: str
    username: str
    venmo_user_id: str


class PayPalAccount(CreditCard):
    """
    https://developer.paypal.com/braintree/docs/reference/response/paypal-account
    """

    billing_agreement_id: str
    email: str
    payer_id: str
    revoked_at: datetime


class USBankAccount(CreditCard):
    """
    https://developer.paypal.com/braintree/docs/reference/response/us-bank-account
    """

    account_holder_name: str
    account_type: str
    ach_mandate: str
    bank_name: str
    business_name: str
    last_name: str
    owner_id: str
    ownership_type: str
    plaid_verified_at: datetime
    routing_number: str
    verifiable: bool
    verified: bool


PaymentMethod = Union[
    CreditCard, AndroidPayCard, ApplePayCard, SamsungPayCard, USBankAccount, PayPalAccount, VenmoAccount, VisaCheckoutCard
]
